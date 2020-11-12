#!/usr/bin/env bash
# A script for building RPM packages.

trap 'exit 100' INT

if [ "$#" -lt 1 ]; then
    echo 'USAGE: ./build.sh <package>|clean'
    echo 'EXAMPLE: ./build.sh tomcat'
    exit 0
fi

if [ "$1" == "clean" ]; then
    rm -rf build build.log >/dev/null 2>&1
    exit 0
fi

# --------------- Setup ----------------

package="$1"

# Clear any existing log files.
echo -n '' > build.log

# Define some utility functions for printing and logging.
print_sec() { echo ":: $@"; echo "$@" >> build.log; }
print_sec_err() { echo ":: $@" 1>&2; echo "$@" >> build.log; }
print_nosec() { echo "   $@"; echo "$@" >> build.log; }
print_nosec_err() { echo "   $@" 1>&2; echo "$@" >> build.log; }
print_subsec() { echo "  --> $@"; echo "$@" >> build.log; }
print_subsec_err() { echo "  --> $@" 1>&2; echo "$@" >> build.log; }
print_nosubsec() { echo "      $@"; echo "$@" >> build.log; }
print_nosubsec_err() { echo "      $@" 1>&2; echo "$@" >> build.log; }
print_subsubsec() { echo "        * $@"; echo "$@" >> build.log; }
print_subsubsec_err() { echo "        * $@" 1>&2; echo "$@" >> build.log; }

# A string that is commonly used.
n0ec='subprocess returned non-zero exit code.'

# The name of the docker image that is created.
image='harrison/build-rpm'

# Some coputed paths
package_dir="src/$package"
spec_file="$package_dir/${package}.spec"

# --------------------------------------


# -------- Validate Environment --------

EC=1
print_sec "Validating environment..."

print_subsec "Validating required binaries..."
for b in docker; do
    if ! command -v "$b" >/dev/null 2>&1; then
        print_nosubsec_err "Error: Required binary \"$b\" is not installed."
        exit $EC
    fi
done

print_subsec "Validating docker file..."
if [ ! -f Dockerfile ]; then
    print_nosubsec_err "Error: Required \"Dockerfile\" file not found in the current working directory."
    exit $EC
fi

print_subsec "Validating package directory..."
if [ ! -d "$package_dir" ]; then
    print_nosubsec_err "Error: Package directory \"$package_dir\" does not exist."
    exit $EC
fi

print_subsec "Validating SPEC file..."
if [ ! -f "$spec_file" ]; then
    print_nosubsec_err "Error: Package SPEC file \"$spec_file\" does not exist."
    exit $EC
fi

print_subsec "Checking for running container instances..."
if docker container ls | grep -q 'build-rpm'; then
    if ! docker container kill build-rpm >/dev/null 2>>build.log; then
        print_nosubsec_err "Error: Unable to kill existing container instance - ${n0ec}"
        exit $EC
    fi
    sleep 5
fi

# --------------------------------------


# --------- Build Docker Image ---------

EC=2
print_sec "Building docker image..."

if ! docker build -t "${image}:latest" . >> build.log 2>&1; then
    print_nosec_err "Error: Unable to build docker image - ${n0ec}"
    exit $EC
fi

# --------------------------------------


# ---------- Run Docker Image ----------

EC=3
print_sec "Running docker image..."

docker='docker run --rm -t -d --name build-rpm'
mounts="-v ${PWD}/build:/root/rpmbuild/RPMS/x86_64"

print_subsec "Setting-up mount points..."
if [ ! -d build ]; then
    if ! mkdir build >> build.log 2>&1; then
        print_nosubsec_err "Error: Unable to create \"build\" directory - $n0ec"
        exit $EC
    fi
fi

print_subsec "Instantiating daemonized image..."
if ! $docker $mounts "$image" >> build.log 2>&1; then
    print_nosubsec_err "Error: Unable to instantiate daemonized image - ${n0ec}"
    exit $EC
fi

# Sleep for a bit
sleep 3

# --------------------------------------


# ----------- Import Package -----------

EC=4
print_sec "Importing package..."

print_subsec "Importing SPEC file..."
if ! docker cp "$spec_file" "build-rpm:/root/rpmbuild/SPECS/" >> build.log 2>&1; then
    print_nosubsec_err "Error: Unable to import SPEC file - $n0ec"
    exit $EC
fi

print_subsec "Importing sources..."
if ! docker cp "$package_dir/." "build-rpm:/root/rpmbuild/SOURCES" >> build.log 2>&1; then
    print_nosubsec_err "Error: Unable to import sources - $n0ec"
    exit $EC
fi

# --------------------------------------


# ----------- Build Package ------------

EC=5
print_sec "Building package..."

de='docker exec -t build-rpm'

print_subsec "Installing build dependencies..."
if ! $de /usr/bin/yum-builddep -y "SPECS/${package}.spec" >> build.log 2>&1; then
    print_nosubsec_err "Error: Unable to install build dependencies - $n0ec"
    exit $EC
fi

print_subsec "Fetching remote sources..."
if ! $de /usr/bin/spectool -g -C SOURCES "SPECS/${package}.spec" >> build.log 2>&1; then
    print_nosubsec_err "Error: Unable to fetch remote sources - $n0ec"
    exit $EC
fi

print_subsec "Building package..."
if ! $de /usr/bin/rpmbuild -bb "SPECS/${package}.spec" >> build.log 2>&1; then
    print_nosubsec_err "Error: Unable to build package - $n0ec"
    exit $EC
fi

# --------------------------------------


# -------------- Cleanup ---------------

EC=6
print_sec "Cleaning up..."

print_subsec "Killing daemonized image..."
if ! docker container kill build-rpm >> build.log 2>&1; then
    print_nosubsec_err "Error: Unable to kill daemonized image - ${n0ec}"
    exit $EC
fi

# --------------------------------------
