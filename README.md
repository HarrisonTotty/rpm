# Web Systems Packages

The following repository contains the sources used to construct a custom RPM
repository. The build process itself leverages Docker containers to construct
RPM packages with the `build.sh` script.

## Developing Packages

When developing a package, simply create a new directory within `src`
corresponding to the name of the resulting package. Ensure that the SPEC file
also corresponds to the name of package (appended with `.spec`, of course).
There is no need to separate the `.spec` file from the rest of the sources, as
the build script will do this automatically. It should be noted that `spectool`
is used during the build process, so `Source` declarations may reference remote
locations.

## Building Packages

To build a package, simply execute `build.sh` at the root of this repository
with a single positional argument corresponding to the name of the package you
wish to build. The script will automatically build and launch a Docker-based
build environment based on CentOS 8, and will import the SPEC file and
additional sources relevant to the package (from the `src/${package}`
directory).

``` bash
./build.sh tomcat
```

In the example above, the build script will automatically build the package
associated with the `src/tomcat` directory relative to the root of this
repository. This will result in one or more `.rpm` packages being placed in a
directory called `build/`. Note that these packages are created with ownership
`root:root` with the intent of simplifying the synchronization process. If the
build process fails, you can find more info in the generated `build.log`.
