// samurai-gallery :: __SLUG__
// SPDX-License-Identifier: BSD-3-Clause

#include <filesystem>
#include <string>

#include <samurai/algorithm.hpp>
#include <samurai/arguments.hpp>
#include <samurai/field.hpp>
#include <samurai/io/hdf5.hpp>
#include <samurai/mr/adapt.hpp>
#include <samurai/mr/mesh.hpp>
#include <samurai/samurai.hpp>

namespace fs = std::filesystem;

template <class Field>
void save_frame(const fs::path& path, const std::string& filename, const Field& u, std::size_t frame)
{
    samurai::save(path, fmt::format("{}_{:04d}", filename, frame), u.mesh(), u);
}

int main(int argc, char* argv[])
{
    samurai::initialize("samurai-gallery: __TITLE__", argc, argv);

    // Output parameters (the driver passes --path/--filename/--nfiles).
    fs::path path        = fs::current_path();
    std::string filename = "__SLUG__";
    std::size_t nfiles   = 40;

    auto& app = samurai::app;
    app.add_option("--path", path, "Output path")->capture_default_str()->group("Output");
    app.add_option("--filename", filename, "File name prefix")->capture_default_str()->group("Output");
    app.add_option("--nfiles", nfiles, "Number of output frames")->capture_default_str()->group("Output");
    SAMURAI_PARSE(argc, argv);

    // TODO: build the mesh, set the initial condition, run the time loop,
    //       and call save_frame(...) nfiles times.
    //
    // See cases/getting-started/advection-2d/main.cpp for a complete example.

    samurai::finalize();
    return 0;
}
