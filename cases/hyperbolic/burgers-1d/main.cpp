// samurai-gallery :: hyperbolic/burgers-1d
// SPDX-License-Identifier: BSD-3-Clause
//
// 1D inviscid Burgers equation: a smooth "hat" steepens into a shock,
// captured on an adaptive (multiresolution) mesh.

#include <cmath>
#include <filesystem>
#include <string>

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
    auto& app = samurai::initialize("samurai-gallery: 1D Burgers equation", argc, argv);

    static constexpr std::size_t dim    = 1;
    static constexpr std::size_t n_comp = 1;
    using Box                           = samurai::Box<double, dim>;

    double left_box       = -1.0;
    double right_box      = 1.0;
    double Tf             = 1.0;
    double cfl            = 0.95;
    std::size_t min_level = 2;
    std::size_t max_level = 9;

    fs::path path        = fs::current_path();
    std::string filename = "burgers_1d";
    std::size_t nfiles   = 60;

    app.add_option("--Tf", Tf, "Final time")->capture_default_str()->group("Simulation");
    app.add_option("--cfl", cfl, "CFL number")->capture_default_str()->group("Simulation");
    app.add_option("--path", path, "Output path")->capture_default_str()->group("Output");
    app.add_option("--filename", filename, "File name prefix")->capture_default_str()->group("Output");
    app.add_option("--nfiles", nfiles, "Number of output frames")->capture_default_str()->group("Output");
    SAMURAI_PARSE(argc, argv);

    typename Box::point_t c1, c2;
    c1.fill(left_box);
    c2.fill(right_box);
    Box box(c1, c2);

    auto config = samurai::mesh_config<dim>().min_level(min_level).max_level(max_level).max_stencil_size(6);
    auto mesh   = samurai::mra::make_mesh(box, config);

    auto u    = samurai::make_vector_field<n_comp>("u", mesh);
    auto u1   = samurai::make_vector_field<n_comp>("u1", mesh);
    auto u2   = samurai::make_vector_field<n_comp>("u2", mesh);
    auto unp1 = samurai::make_vector_field<n_comp>("unp1", mesh);

    u.resize();
    // "Hat" initial condition: triangular bump on [-0.5, 0.5].
    samurai::for_each_cell(mesh,
                           [&](auto& cell)
                           {
                               const double max = 1.0;
                               const double r   = 0.5;
                               const double d   = std::abs(cell.center(0));
                               u[cell]          = (d <= r) ? (-max / r * d + max) : 0.0;
                           });

    samurai::make_bc<samurai::Dirichlet<3>>(u, 0.0);
    u1.copy_bc_from(u);
    u2.copy_bc_from(u);

    // Burgers flux f(u) = u^2 / 2.
    auto conv = 0.5 * samurai::make_convection_weno5<decltype(u)>();

    const double dx = mesh.min_cell_length();
    const double dt = cfl * dx / 2.0;

    auto MRadaptation = samurai::make_MRAdapt(u);
    auto mra_config   = samurai::mra_config();
    MRadaptation(mra_config);

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

        MRadaptation(mra_config);
        u1.resize();
        u2.resize();
        unp1.resize();

        // TVD-RK3 (SSPRK3)
        u1   = u - step * conv(u);
        u2   = 3. / 4 * u + 1. / 4 * (u1 - step * conv(u1));
        unp1 = 1. / 3 * u + 2. / 3 * (u2 - step * conv(u2));
        samurai::swap(u, unp1);

        std::cout << fmt::format("iteration {}: t = {:.3f}, dt = {:.5f}", nt++, t, step) << std::endl;

        if (t >= next_save - 1e-12 || t >= Tf)
        {
            save_frame(path, filename, u, frame++);
            next_save += dt_save;
        }
    }

    samurai::finalize();
    return 0;
}
