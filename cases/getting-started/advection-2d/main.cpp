// Copyright 2018-2025 the samurai's authors
// SPDX-License-Identifier:  BSD-3-Clause
//
// samurai-gallery :: getting-started/advection-2d
// Linear advection of a disc on an adaptive (multiresolution) mesh.

#include <array>
#include <cmath>
#include <filesystem>
#include <limits>

#include <xtensor/containers/xfixed.hpp>

#include <samurai/algorithm.hpp>
#include <samurai/arguments.hpp>
#include <samurai/bc.hpp>
#include <samurai/field.hpp>
#include <samurai/io/hdf5.hpp>
#include <samurai/mr/adapt.hpp>
#include <samurai/mr/mesh.hpp>
#include <samurai/samurai.hpp>
#include <samurai/stencil_field.hpp>
#include <samurai/subset/node.hpp>

namespace fs = std::filesystem;

template <class Field>
void init(Field& u, double radius, double x_center, double y_center)
{
    auto& mesh = u.mesh();
    u.resize();

    samurai::for_each_cell(mesh,
                           [&](auto& cell)
                           {
                               const auto center = cell.center();
                               const double dx    = center[0] - x_center;
                               const double dy    = center[1] - y_center;
                               u[cell]            = (dx * dx + dy * dy <= radius * radius) ? 1. : 0.;
                           });
}

template <class Field>
void save_frame(const fs::path& path, const std::string& filename, const Field& u, std::size_t frame)
{
    auto& mesh = u.mesh();
    samurai::save(path, fmt::format("{}_{:04d}", filename, frame), mesh, u);
}

int main(int argc, char* argv[])
{
    samurai::initialize("samurai-gallery: 2D linear advection on a multiresolution mesh", argc, argv);

    constexpr std::size_t dim              = 2;
    constexpr std::size_t pred_stencil_size = 1;

    // Simulation parameters
    xt::xtensor_fixed<double, xt::xshape<dim>> min_corner = {0., 0.};
    xt::xtensor_fixed<double, xt::xshape<dim>> max_corner = {1., 1.};
    std::array<double, dim> a{
        {1., 1.}
    };
    double Tf          = 0.6;
    double cfl         = 0.5;
    double radius      = 0.15;
    double x_center    = 0.3;
    double y_center    = 0.3;
    std::size_t min_level = 4;
    std::size_t max_level = 10;
    double mr_epsilon  = 2e-4;

    // Output parameters
    fs::path path        = fs::current_path();
    std::string filename = "advection_2d";
    std::size_t nfiles   = 50;

    auto& app = samurai::app;
    app.add_option("--min-corner", min_corner, "The min corner of the box")->capture_default_str()->group("Simulation");
    app.add_option("--max-corner", max_corner, "The max corner of the box")->capture_default_str()->group("Simulation");
    app.add_option("--velocity", a, "Advection velocity")->capture_default_str()->group("Simulation");
    app.add_option("--cfl", cfl, "CFL number")->capture_default_str()->group("Simulation");
    app.add_option("--Tf", Tf, "Final time")->capture_default_str()->group("Simulation");
    app.add_option("--radius", radius, "Initial disc radius")->capture_default_str()->group("Simulation");
    app.add_option("--x-center", x_center, "Initial disc center (x)")->capture_default_str()->group("Simulation");
    app.add_option("--y-center", y_center, "Initial disc center (y)")->capture_default_str()->group("Simulation");
    app.add_option("--path", path, "Output path")->capture_default_str()->group("Output");
    app.add_option("--filename", filename, "File name prefix")->capture_default_str()->group("Output");
    app.add_option("--nfiles", nfiles, "Number of output frames")->capture_default_str()->group("Output");
    // --min-level, --max-level and --mr-eps are provided natively by samurai.
    SAMURAI_PARSE(argc, argv);

    // Pick up samurai's native adaptation options when the user set them.
    if (samurai::args::min_level != std::numeric_limits<std::size_t>::max())
    {
        min_level = samurai::args::min_level;
    }
    if (samurai::args::max_level != std::numeric_limits<std::size_t>::max())
    {
        max_level = samurai::args::max_level;
    }
    if (std::isfinite(samurai::args::epsilon))
    {
        mr_epsilon = samurai::args::epsilon;
    }

    const samurai::Box<double, dim> box(min_corner, max_corner);
    auto config = samurai::mesh_config<dim, pred_stencil_size>()
                      .min_level(min_level)
                      .max_level(max_level)
                      .max_stencil_size(2)
                      .disable_minimal_ghost_width();
    auto mesh = samurai::mra::make_mesh(box, config);

    auto u = samurai::make_scalar_field<double>("u", mesh);
    init(u, radius, x_center, y_center);
    samurai::make_bc<samurai::Dirichlet<1>>(u, 0.);

    auto unp1         = samurai::make_scalar_field<double>("unp1", mesh);
    auto MRadaptation = samurai::make_MRAdapt(u);
    auto mra_config   = samurai::mra_config().epsilon(mr_epsilon);
    MRadaptation(mra_config);

    const double dt      = cfl * mesh.min_cell_length();
    const double dt_save = Tf / static_cast<double>(nfiles > 1 ? nfiles - 1 : 1);

    std::size_t frame = 0;
    save_frame(path, filename, u, frame++);

    double t          = 0.;
    double next_save  = dt_save;
    std::size_t nt    = 0;
    while (t < Tf)
    {
        MRadaptation(mra_config);

        double step = dt;
        if (t + step > Tf)
        {
            step = Tf - t;
        }
        t += step;

        samurai::update_ghost_mr(u);
        unp1.resize();
        unp1 = u - step * samurai::upwind(a, u);
        std::swap(u.array(), unp1.array());

        std::cout << fmt::format("iteration {}: t = {:.5f}, dt = {:.5f}", nt++, t, step) << std::endl;

        if (t >= next_save - 1e-12 || t >= Tf)
        {
            save_frame(path, filename, u, frame++);
            next_save += dt_save;
        }
    }

    samurai::finalize();
    return 0;
}
