// samurai-gallery :: transport/linear-convection-obstacle
// SPDX-License-Identifier: BSD-3-Clause
//
// A square profile is advected diagonally across a domain that has a
// rectangular obstacle carved out of it. WENO5 + TVD-RK3, multiresolution.

#include <filesystem>
#include <string>

#include <samurai/domain_builder.hpp>
#include <samurai/io/hdf5.hpp>
#include <samurai/mr/adapt.hpp>
#include <samurai/mr/mesh.hpp>
#include <samurai/samurai.hpp>
#include <samurai/schemes/fv.hpp>

namespace fs = std::filesystem;

template <class Field>
void save_frame(const fs::path& path, const std::string& filename, const Field& u, std::size_t frame)
{
    auto& mesh  = u.mesh();
    auto level_ = samurai::make_scalar_field<std::size_t>("level", mesh);
    samurai::for_each_cell(mesh,
                           [&](const auto& cell)
                           {
                               level_[cell] = cell.level;
                           });
    samurai::save(path, fmt::format("{}_{:04d}", filename, frame), mesh, u, level_);
}

int main(int argc, char* argv[])
{
    auto& app = samurai::initialize("samurai-gallery: linear convection around an obstacle", argc, argv);

    static constexpr std::size_t dim = 2;

    double Tf             = 3.0;
    double cfl            = 0.95;
    std::size_t min_level = 2;
    std::size_t max_level = 6;

    fs::path path        = fs::current_path();
    std::string filename = "linear_convection_obstacle";
    std::size_t nfiles   = 60;

    app.add_option("--Tf", Tf, "Final time")->capture_default_str()->group("Simulation");
    app.add_option("--cfl", cfl, "CFL number")->capture_default_str()->group("Simulation");
    app.add_option("--path", path, "Output path")->capture_default_str()->group("Output");
    app.add_option("--filename", filename, "File name prefix")->capture_default_str()->group("Output");
    app.add_option("--nfiles", nfiles, "Number of output frames")->capture_default_str()->group("Output");
    SAMURAI_PARSE(argc, argv);

    // Domain [-1,1]^2 with a square obstacle removed.
    samurai::DomainBuilder<dim> domain({-1., -1.}, {1., 1.});
    domain.remove({0.0, 0.0}, {0.4, 0.4});

    auto config = samurai::mesh_config<dim>().min_level(min_level).max_level(max_level).max_stencil_size(6);
    auto mesh   = samurai::mra::make_mesh(domain, config);

    auto u = samurai::make_scalar_field<double>("u",
                                                mesh,
                                                [](const auto& coords)
                                                {
                                                    const auto& x = coords(0);
                                                    const auto& y = coords(1);
                                                    return (x >= -0.8 && x <= -0.3 && y >= 0.3 && y <= 0.8) ? 1. : 0.;
                                                });

    auto unp1 = samurai::make_scalar_field<>("unp1", mesh);
    auto u1   = samurai::make_scalar_field<>("u1", mesh);
    auto u2   = samurai::make_scalar_field<>("u2", mesh);

    samurai::VelocityVector<dim> constant_velocity = {1, -1};
    auto velocity = samurai::make_vector_field<dim>("velocity",
                                                    mesh,
                                                    [&](const auto&)
                                                    {
                                                        return constant_velocity;
                                                    });

    samurai::make_bc<samurai::Dirichlet<1>>(velocity, 0., 0.); // wall
    samurai::make_bc<samurai::Dirichlet<3>>(u, 0.);
    u1.copy_bc_from(u);
    u2.copy_bc_from(u);

    auto conv = samurai::make_convection_weno5<decltype(u)>(velocity);

    const double dx = mesh.min_cell_length();
    const double dt = cfl * dx / xt::sum(xt::abs(constant_velocity))();

    auto MRadaptation = samurai::make_MRAdapt(u);
    auto mra_config   = samurai::mra_config().epsilon(1e-3);
    MRadaptation(mra_config, velocity);

    const double dt_save = Tf / static_cast<double>(nfiles > 1 ? nfiles - 1 : 1);
    std::size_t frame    = 0;
    save_frame(path, filename, u, frame++);

    double t         = 0.;
    double next_save = dt_save;
    std::size_t nt   = 0;
    while (t < Tf)
    {
        double step = dt;
        if (t + step > Tf)
        {
            step = Tf - t;
        }
        t += step;

        MRadaptation(mra_config, velocity);
        samurai::for_each_cell(mesh,
                               [&](const auto& cell)
                               {
                                   velocity[cell] = constant_velocity;
                               });
        samurai::update_ghost_mr(velocity);
        unp1.resize();
        u1.resize();
        u2.resize();

        // TVD-RK3 (SSPRK3)
        u1   = u - step * conv(u);
        u2   = 3. / 4 * u + 1. / 4 * (u1 - step * conv(u1));
        unp1 = 1. / 3 * u + 2. / 3 * (u2 - step * conv(u2));
        samurai::swap(u, unp1);

        std::cout << fmt::format("iteration {}: t = {:.3f}, dt = {:.4f}", nt++, t, step) << std::endl;

        if (t >= next_save - 1e-12 || t >= Tf)
        {
            save_frame(path, filename, u, frame++);
            next_save += dt_save;
        }
    }

    samurai::finalize();
    return 0;
}
