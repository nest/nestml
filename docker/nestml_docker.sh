#!/bin/sh


# We expect either a valid command ('provision' or 'run') or '--help'
# as the first argument to the script. If '--help' is provided or an
# invalid command, we print usage information
if test $# -lt 1; then
    print_usage=true
else
    case "$1" in
	provision)
	    mode=provision
	    ;;
	run)
	    mode=run
	    ;;
	--help)
	    print_usage=true
	    ;;
	*)
	    echo "Error: unknown command '$1'"
	    print_usage=true
	    ;;
    esac
    shift
fi

# Print usage information
if test x$print_usage = xtrue; then
    echo "Usage: nestml_docker.sh [--help] <command> [<args>]"
    echo "  --help    print this usage information."
    echo "  <command> can be either 'provision' or 'run'."
    echo
    echo "  Use 'nestml_docker.sh <command> --help' to print detailed"
    echo "  usage information for <command>."
    echo
    exit 1
fi

# Executing the command
case $mode in
    provision)
	# For the 'provision' command, we allow the following arguments:
	#  --help  print usage information for the 'run' command
	#  --dev   use the development container instead of the
	#          release version
	container="nestml_release"
	dockerfile="DockerfileRelease"
	while test $# -gt 0; do
	    case "$1" in
		--help)
		    print_usage=true
		    ;;
		--dev)
		    container="nestml_development"
		    dockerfile="DockerfileDevelopment"
		    ;;
		*)
		    echo "Error: Unrecognized option '$1'"
		    print_usage=true
		    ;;
	    esac
	    shift
	done

	# Print usage information
	if test x$print_usage = xtrue; then
	    echo "Usage: nestml_docker.sh provision [<args>]"
	    echo "  --dev  Use the development version"
	    echo "  --help  Print this usage information"
	    exit 1
	fi

	# Provision the docker container
	cmd="docker build -t $container -f $dockerfile"
	echo
	echo "Creating docker image '$container'"
	echo $cmd
	;;
    run)
	# For the 'run' command, we allow the following arguments:
	#  --help  print usage information for the 'run' command
	#  --dev   use the development container instead of the
	#          release version
	#  dir(s)  one or more directories with .nestml files
	container="nestml_release"
	while test $# -gt 0; do
	    case "$1" in
		--help)
		    print_usage=true
		    ;;
		--dev)
		    container="nestml_development"
		    ;;
		*)
		    # If the argument is a valid directory, we safe
		    # the absolut path of it, else, we only print a
		    # corresponding error message and go on parsing.
		    if test -d $1; then
			src="`cd $1; pwd` $src"
		    else
			echo "Error: '$1' is not a directory"
		    fi
		    ;;
	    esac
	    shift
	done

	# If no valid source directory was given, we print usage
	# information
	if test "x$src" = x; then
	    print_usage=true
	fi

	# Print usage information
	if test x$print_usage = xtrue; then
	    echo "Usage: nestml_docker.sh run [<args>] <dir1> [<dir2> ...]"
	    echo "  --dev   Use the development version"
	    echo "  --help  Print this usage information"
	    echo "  <dir1>, <dir2>, ...  Source directories"
	    exit 1
	fi

	# Run the docker container for each of the given valid source
	# directories
	for dir in $src; do
	    mnt=`basename $dir`
	    uid="-e UID="`id -u`
	    vol="-v $dir:/$mnt"
	    opt="/$mnt --target /$mnt/build"
	    cmd="docker run $vol $uid $container $opt"
	    echo
	    echo "Running docker image '$container'"
	    echo $cmd
	done
	;;
esac
