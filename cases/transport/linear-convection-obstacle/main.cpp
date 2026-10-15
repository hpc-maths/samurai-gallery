// samurai-gallery :: transport/linear-convection-obstacle
// SPDX-License-Identifier: BSD-3-Clause
//
// A square profile is carried by a diagonal flow that goes around a square
// obstacle carved out of the domain. WENO5 + TVD-RK3, multiresolution.

#include <algorithm>
#include <cmath>
#include <filesystem>
#include <string>

#include <samurai/domain_builder.hpp>
#include <samurai/io/hdf5.hpp>
#include <samurai/mr/adapt.hpp>
#include <samurai/mr/mesh.hpp>
#include <samurai/samurai.hpp>
#include <samurai/schemes/fv.hpp>

namespace fs = std::filesystem;

// Obstacle: the square [0, 0.4]^2.
constexpr double obstacle_center = 0.2;
constexpr double obstacle_half   = 0.2;
// Distance over which the flow bends around the obstacle.
constexpr double bend_length = 0.15;

// Stream function of the flow. Far from the obstacle it is x + y - 0.4, the
// uniform velocity (1, -1); it vanishes on the obstacle boundary, so the
// obstacle is a streamline and no flow crosses it. The velocity derived from
// it is divergence free: the profile is carried around the obstacle without
// being compressed against it.
double stream_function(double x, double y)
{
    const double dx = std::max(std::abs(x - obstacle_center) - obstacle_half, 0.);
    const double dy = std::max(std::abs(y - obstacle_center) - obstacle_half, 0.);
    const double d  = std::hypot(dx, dy); // distance to the obstacle
    return (x + y - 2 * obstacle_center) * (1. - std::exp(-d / bend_length));
}

// Velocity (d psi/dy, -d psi/dx), by centered differences of the stream function.
samurai::Array<double, 2> flow_velocity(double x, double y)
{
    constexpr double h = 1e-7;
    return {(stream_function(x, y + h) - stream_function(x, y - h)) / (2 * h),
            -(stream_function(x + h, y) - stream_function(x - h, y)) / (2 * h)};
}

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

    double Tf             = 1.8;
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
    domain.remove({obstacle_center - obstacle_half, obstacle_center - obstacle_half},
                  {obstacle_center + obstacle_half, obstacle_center + obstacle_half});

    auto config = samurai::mesh_config<dim>().min_level(min_level).max_level(max_level).max_stencil_size(6);
    auto mesh   = samurai::mra::make_mesh(domain, config);

    auto u = samurai::make_scalar_field<double>("u",
                                                mesh,
                                                [](const auto& coords)
                                                {
                                                    const auto& x = coords(0);
                                                    const auto& y = coords(1);
                                                    // A square centered on the streamline x + y = 0.4
                                                    // that hits the obstacle head-on, so the flow
                                                    // splits it in two.
                                                    return (x >= -0.5 && x <= -0.1 && y >= 0.5 && y <= 0.9) ? 1. : 0.;
                                                });

    auto unp1 = samurai::make_scalar_field<>("unp1", mesh);
    auto u1   = samurai::make_scalar_field<>("u1", mesh);
    auto u2   = samurai::make_scalar_field<>("u2", mesh);

    auto velocity = samurai::make_vector_field<dim>("velocity",
                                                    mesh,
                                                    [](const auto& coords)
                                                    {
                                                        return flow_velocity(coords(0), coords(1));
                                                    });

    // The boundary velocity is the flow itself: tangent to the obstacle wall
    // (no flux through it) and (1, -1) on the outer boundary, so the profile
    // leaves the domain instead of piling up in a corner.
    samurai::make_bc<samurai::Dirichlet<1>>(velocity,
                                            [](const auto&, const auto&, const auto& coords)
                                            {
                                                return flow_velocity(coords[0], coords[1]);
                                            });
    samurai::make_bc<samurai::Dirichlet<3>>(u, 0.);
    u1.copy_bc_from(u);
    u2.copy_bc_from(u);

    auto conv = samurai::make_convection_weno5<decltype(u)>(velocity);

    // The flow speeds up around the obstacle: the time step follows the
    // fastest cell of the finest level.
    double max_speed = 0.;
    samurai::for_each_cell(mesh,
                           [&](const auto& cell)
                           {
                               max_speed = std::max(max_speed, xt::sum(xt::abs(velocity[cell]))());
                           });
    const double dx = mesh.min_cell_length();
    const double dt = cfl * dx / max_speed;

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
                                   const auto x   = cell.center();
                                   velocity[cell] = flow_velocity(x[0], x[1]);
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
