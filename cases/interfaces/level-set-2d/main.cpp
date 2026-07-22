// samurai-gallery :: interfaces/level-set-2d
// SPDX-License-Identifier: BSD-3-Clause
//
// Level-set advection in the classic swirling "vortex in a box" velocity
// field. A circular interface is stretched into a thin filament and (at
// t = Tf/2 the flow reverses in the full test) would return to a circle.
// Multiresolution keeps the finest cells on the interface.

#include <cmath>
#include <filesystem>
#include <string>

#include <samurai/algorithm.hpp>
#include <samurai/algorithm/update.hpp>
#include <samurai/bc.hpp>
#include <samurai/box.hpp>
#include <samurai/field.hpp>
#include <samurai/io/hdf5.hpp>
#include <samurai/mr/adapt.hpp>
#include <samurai/mr/mesh.hpp>
#include <samurai/samurai.hpp>
#include <samurai/subset/node.hpp>

#include "level_set_operators.hpp"

namespace fs = std::filesystem;

template <class Field>
void init_level_set(Field& phi)
{
    using mesh_id_t = typename Field::mesh_t::mesh_id_t;
    auto& mesh      = phi.mesh();
    phi.resize();

    samurai::for_each_cell(mesh[mesh_id_t::cells],
                           [&](auto& cell)
                           {
                               const auto center         = cell.center();
                               constexpr double radius   = 0.15;
                               constexpr double x_center = 0.5;
                               constexpr double y_center = 0.75;
                               phi[cell] = std::sqrt(std::pow(center[0] - x_center, 2.) + std::pow(center[1] - y_center, 2.)) - radius;
                           });
    samurai::make_bc<samurai::Neumann<1>>(phi, 0.);
}

template <class Mesh>
auto init_velocity(Mesh& mesh)
{
    using mesh_id_t = typename Mesh::mesh_id_t;
    const double PI = xt::numeric_constants<double>::PI;

    auto u = samurai::make_vector_field<double, 2>("u", mesh);
    u.fill(0);
    samurai::for_each_cell(mesh[mesh_id_t::cells_and_ghosts],
                           [&](auto& cell)
                           {
                               const auto center = cell.center();
                               const double x    = center[0];
                               const double y    = center[1];
                               u[cell][0]        = -std::pow(std::sin(PI * x), 2.) * std::sin(2. * PI * y);
                               u[cell][1]        = std::pow(std::sin(PI * y), 2.) * std::sin(2. * PI * x);
                           });
    samurai::make_bc<samurai::Neumann<1>>(u, 0., 0.);
    return u;
}

template <class Field, class Field_u>
void flux_correction(Field& phi_np1, const Field& phi_n, const Field_u& u, double dt)
{
    using mesh_t              = typename Field::mesh_t;
    using mesh_id_t           = typename mesh_t::mesh_id_t;
    using interval_t          = typename mesh_t::interval_t;
    constexpr std::size_t dim = Field::dim;

    auto& mesh                  = phi_np1.mesh();
    const std::size_t min_level = mesh[mesh_id_t::cells].min_level();
    const std::size_t max_level = mesh[mesh_id_t::cells].max_level();
    for (std::size_t level = min_level; level < max_level; ++level)
    {
        xt::xtensor_fixed<int, xt::xshape<2>> stencil;

        stencil          = {{-1, 0}};
        auto subset_right = samurai::intersection(samurai::translate(mesh[mesh_id_t::cells][level + 1], stencil),
                                                  mesh[mesh_id_t::cells][level])
                                .on(level);
        subset_right(
            [&](const auto& i, const auto& index)
            {
                auto j          = index[0];
                const double dx = mesh.cell_length(level);
                phi_np1(level, i, j) = phi_np1(level, i, j)
                                     + dt / dx
                                           * (samurai::upwind_variable_op<dim, interval_t>(level, i, j).right_flux(u, phi_n, dt)
                                              - .5 * samurai::upwind_variable_op<dim, interval_t>(level + 1, 2 * i + 1, 2 * j).right_flux(u, phi_n, dt)
                                              - .5 * samurai::upwind_variable_op<dim, interval_t>(level + 1, 2 * i + 1, 2 * j + 1).right_flux(u, phi_n, dt));
            });

        stencil         = {{1, 0}};
        auto subset_left = samurai::intersection(samurai::translate(mesh[mesh_id_t::cells][level + 1], stencil),
                                                 mesh[mesh_id_t::cells][level])
                               .on(level);
        subset_left(
            [&](const auto& i, const auto& index)
            {
                auto j          = index[0];
                const double dx = mesh.cell_length(level);
                phi_np1(level, i, j) = phi_np1(level, i, j)
                                     - dt / dx
                                           * (samurai::upwind_variable_op<dim, interval_t>(level, i, j).left_flux(u, phi_n, dt)
                                              - .5 * samurai::upwind_variable_op<dim, interval_t>(level + 1, 2 * i, 2 * j).left_flux(u, phi_n, dt)
                                              - .5 * samurai::upwind_variable_op<dim, interval_t>(level + 1, 2 * i, 2 * j + 1).left_flux(u, phi_n, dt));
            });

        stencil       = {{0, -1}};
        auto subset_up = samurai::intersection(samurai::translate(mesh[mesh_id_t::cells][level + 1], stencil), mesh[mesh_id_t::cells][level])
                             .on(level);
        subset_up(
            [&](const auto& i, const auto& index)
            {
                auto j          = index[0];
                const double dx = mesh.cell_length(level);
                phi_np1(level, i, j) = phi_np1(level, i, j)
                                     + dt / dx
                                           * (samurai::upwind_variable_op<dim, interval_t>(level, i, j).up_flux(u, phi_n, dt)
                                              - .5 * samurai::upwind_variable_op<dim, interval_t>(level + 1, 2 * i, 2 * j + 1).up_flux(u, phi_n, dt)
                                              - .5 * samurai::upwind_variable_op<dim, interval_t>(level + 1, 2 * i + 1, 2 * j + 1).up_flux(u, phi_n, dt));
            });

        stencil         = {{0, 1}};
        auto subset_down = samurai::intersection(samurai::translate(mesh[mesh_id_t::cells][level + 1], stencil),
                                                 mesh[mesh_id_t::cells][level])
                               .on(level);
        subset_down(
            [&](const auto& i, const auto& index)
            {
                auto j          = index[0];
                const double dx = mesh.cell_length(level);
                phi_np1(level, i, j) = phi_np1(level, i, j)
                                     - dt / dx
                                           * (samurai::upwind_variable_op<dim, interval_t>(level, i, j).down_flux(u, phi_n, dt)
                                              - .5 * samurai::upwind_variable_op<dim, interval_t>(level + 1, 2 * i, 2 * j).down_flux(u, phi_n, dt)
                                              - .5 * samurai::upwind_variable_op<dim, interval_t>(level + 1, 2 * i + 1, 2 * j).down_flux(u, phi_n, dt));
            });
    }
}

template <class Phi>
void save_frame(const fs::path& path, const std::string& filename, const Phi& phi, std::size_t frame)
{
    auto& mesh  = phi.mesh();
    auto level_ = samurai::make_scalar_field<std::size_t>("level", mesh);
    samurai::for_each_cell(mesh,
                           [&](const auto& cell)
                           {
                               level_[cell] = cell.level;
                           });
    samurai::save(path, fmt::format("{}_{:04d}", filename, frame), mesh, phi, level_);
}

int main(int argc, char* argv[])
{
    auto& app = samurai::initialize("samurai-gallery: level-set advection in a vortex flow", argc, argv);

    constexpr std::size_t dim = 2;

    xt::xtensor_fixed<double, xt::xshape<dim>> min_corner = {0., 0.};
    xt::xtensor_fixed<double, xt::xshape<dim>> max_corner = {1., 1.};
    double Tf             = 3.14;
    double cfl            = 5. / 8;
    std::size_t min_level = 4;
    std::size_t max_level = 8;

    fs::path path        = fs::current_path();
    std::string filename = "level_set_2d";
    std::size_t nfiles   = 80;

    app.add_option("--cfl", cfl, "CFL number")->capture_default_str()->group("Simulation");
    app.add_option("--Tf", Tf, "Final time")->capture_default_str()->group("Simulation");
    app.add_option("--path", path, "Output path")->capture_default_str()->group("Output");
    app.add_option("--filename", filename, "File name prefix")->capture_default_str()->group("Output");
    app.add_option("--nfiles", nfiles, "Number of output frames")->capture_default_str()->group("Output");
    SAMURAI_PARSE(argc, argv);

    const samurai::Box<double, dim> box(min_corner, max_corner);
    auto config = samurai::mesh_config<dim>().min_level(min_level).max_level(max_level).start_level(max_level).max_stencil_radius(2);
    auto mesh   = samurai::mra::make_mesh(box, config);

    auto phi = samurai::make_scalar_field<double>("phi", mesh);
    init_level_set(phi);

    auto u      = init_velocity(mesh);
    auto phinp1 = samurai::make_scalar_field<double>("phi", mesh);
    auto phihat = samurai::make_scalar_field<double>("phi", mesh);
    samurai::make_bc<samurai::Neumann<1>>(phihat, 0.);
    auto rho = samurai::make_scalar_field<double>("rho", mesh, 0.);
    samurai::make_bc<samurai::Neumann<1>>(rho, 0.);

    auto MRadaptation = samurai::make_MRAdapt(rho);
    auto mra_config   = samurai::mra_config().epsilon(1e-2).regularity(1.);

    const double dt      = cfl * mesh.min_cell_length();
    const double dt_save = Tf / static_cast<double>(nfiles > 1 ? nfiles - 1 : 1);

    std::size_t frame = 0;
    save_frame(path, filename, phi, frame++);

    double t         = 0.;
    double next_save = dt_save;
    std::size_t nt   = 0;
    while (t < Tf)
    {
        if (mesh.max_level() > mesh.min_level())
        {
            samurai::for_each_cell(mesh,
                                   [&](const auto& cell)
                                   {
                                       rho[cell] = (phi[cell] > 0.) ? 1000. : 1.;
                                   });
            MRadaptation(mra_config, phi, u);
        }

        double step = dt;
        if (t + step > Tf)
        {
            step = Tf - t;
        }
        t += step;

        // Transport of the level set.
        samurai::update_ghost_mr(phi, u);
        phinp1.resize();
        phinp1 = phi - step * samurai::upwind_variable(u, phi, step);
        flux_correction(phinp1, phi, u, step);
        std::swap(phi.array(), phinp1.array());

        // Reinitialization (a few fictitious TVD-RK2 steps of |grad phi| = 1).
        const std::size_t fict_iteration = 2;
        const double dt_fict             = 0.01 * step;
        auto phi_0                       = phi;
        for (std::size_t k = 0; k < fict_iteration; ++k)
        {
            samurai::update_ghost_mr(phi);
            phihat.resize();
            phihat = phi - dt_fict * H_wrap(phi, phi_0, mesh.max_level());
            samurai::update_ghost_mr(phihat);
            phinp1 = .5 * phi_0 + .5 * (phihat - dt_fict * H_wrap(phihat, phi_0, mesh.max_level()));
            std::swap(phi.array(), phinp1.array());
        }

        std::cout << fmt::format("iteration {}: t = {:.4f}, dt = {:.5f}", nt++, t, step) << std::endl;

        if (t >= next_save - 1e-12 || t >= Tf)
        {
            save_frame(path, filename, phi, frame++);
            next_save += dt_save;
        }
    }

    samurai::finalize();
    return 0;
}
