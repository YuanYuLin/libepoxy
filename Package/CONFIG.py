import ops
import iopc

TARBALL_FILE="libepoxy-1.5.2.tar.xz"
TARBALL_DIR="libepoxy-1.5.2"
INSTALL_DIR="libepoxy-bin"
pkg_path = ""
output_dir = ""
tarball_pkg = ""
tarball_dir = ""
install_dir = ""
install_tmp_dir = ""
cc_host = ""
tmp_include_dir = ""
dst_include_dir = ""
dst_lib_dir = ""
dst_usr_local_lib_dir = ""

def set_global(args):
    global pkg_path
    global output_dir
    global tarball_pkg
    global install_dir
    global install_tmp_dir
    global tarball_dir
    global cc_host
    global tmp_include_dir
    global dst_include_dir
    global dst_lib_dir
    global dst_usr_local_lib_dir
    global dst_usr_local_libexec_dir
    global dst_usr_local_share_dir
    global src_pkgconfig_dir
    global dst_pkgconfig_dir
    global dst_bin_dir
    global dst_etc_dir
    global install_test_utils
    pkg_path = args["pkg_path"]
    output_dir = args["output_path"]
    tarball_pkg = ops.path_join(pkg_path, TARBALL_FILE)
    install_dir = ops.path_join(output_dir, INSTALL_DIR)
    install_tmp_dir = ops.path_join(output_dir, INSTALL_DIR + "-tmp")
    tarball_dir = ops.path_join(output_dir, TARBALL_DIR)
    cc_host_str = ops.getEnv("CROSS_COMPILE")
    cc_host = cc_host_str[:len(cc_host_str) - 1]
    tmp_include_dir = ops.path_join(output_dir, ops.path_join("include",args["pkg_name"]))
    dst_include_dir = ops.path_join("include",args["pkg_name"])
    dst_lib_dir = ops.path_join(install_dir, "lib")
    dst_bin_dir = ops.path_join(install_dir, "bin")
    dst_etc_dir = ops.path_join(install_dir, "etc")
    dst_usr_local_lib_dir = ops.path_join(install_dir, "usr/local/lib")
    dst_usr_local_libexec_dir = ops.path_join(install_dir, "usr/local/libexec")
    dst_usr_local_share_dir = ops.path_join(install_dir, "usr/local/share")
    src_pkgconfig_dir = ops.path_join(pkg_path, "pkgconfig")
    dst_pkgconfig_dir = ops.path_join(install_dir, "pkgconfig")
    if ops.getEnv("INSTALL_TEST_UTILS") == 'y':
        install_test_utils = True
    else:
        install_test_utils = False


def MAIN_ENV(args):
    set_global(args)

    ops.exportEnv(ops.setEnv("CC", ops.getEnv("CROSS_COMPILE") + "gcc"))
    ops.exportEnv(ops.setEnv("CXX", ops.getEnv("CROSS_COMPILE") + "g++"))
    ops.exportEnv(ops.setEnv("CROSS", ops.getEnv("CROSS_COMPILE")))
    ops.exportEnv(ops.setEnv("DESTDIR", install_tmp_dir))

    return False

def MAIN_EXTRACT(args):
    set_global(args)

    ops.unTarXz(tarball_pkg, output_dir)

    return True

def MAIN_PATCH(args, patch_group_name):
    set_global(args)
    for patch in iopc.get_patch_list(pkg_path, patch_group_name):
        if iopc.apply_patch(tarball_dir, patch):
            continue
        else:
            sys.exit(1)

    return True

def MAIN_CONFIGURE(args):
    set_global(args)

    extra_conf = []
    extra_conf.append("--disable-x11")
    extra_conf.append("--host=" + cc_host)

    cc_sysroot = ops.getEnv("CC_SYSROOT")
    cflags = ""
    cflags += " -I" + ops.path_join(cc_sysroot, 'usr/include')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libz')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libpcre3')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libpixman')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libxml2')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libglib')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libglib/glib-2.0')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/mesa')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/mesa/EGL')

    libs = ""
    libs += " -L" + ops.path_join(cc_sysroot, 'lib')
    libs += " -L" + ops.path_join(cc_sysroot, 'usr/lib')
    libs += " -L" + ops.path_join(iopc.getSdkPath(), 'lib')
    libs += " -lz -lglib-2.0 -lpcre -lffi -lpixman-1 -lxml2 -lgbm -ldrm -lEGL -lgbm -lexpat -lglapi" 
    extra_conf.append("CFLAGS=" + cflags)
    extra_conf.append("LDFLAGS=" + libs)
    extra_conf.append("--enable-egl=yes")
    #extra_conf.append("--enable-glx=yes")
    #extra_conf.append("--enable-opengl")
    #extra_conf.append("--enable-virglrenderer")

    iopc.configure(tarball_dir, extra_conf)

    return True

def MAIN_BUILD(args):
    set_global(args)

    ops.mkdir(install_dir)
    ops.mkdir(install_tmp_dir)
    iopc.make(tarball_dir)
    iopc.make_install(tarball_dir)

    ops.mkdir(install_dir)
    ops.mkdir(dst_lib_dir)

    ops.mkdir(dst_lib_dir)
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/lib/libepoxy.so.0.0.0"), dst_lib_dir)
    ops.ln(dst_lib_dir, "libepoxy.so.0.0.0", "libepoxy.so.0.0")
    ops.ln(dst_lib_dir, "libepoxy.so.0.0.0", "libepoxy.so.0")
    ops.ln(dst_lib_dir, "libepoxy.so.0.0.0", "libepoxy.so")

    ops.mkdir(tmp_include_dir)
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/include/."), tmp_include_dir)

    ops.mkdir(dst_pkgconfig_dir)
    ops.copyto(ops.path_join(src_pkgconfig_dir, '.'), dst_pkgconfig_dir)

    return True

def MAIN_INSTALL(args):
    set_global(args)

    iopc.installBin(args["pkg_name"], ops.path_join(ops.path_join(install_dir, "lib"), "."), "lib")
    iopc.installBin(args["pkg_name"], ops.path_join(tmp_include_dir, "."), dst_include_dir)
    iopc.installBin(args["pkg_name"], ops.path_join(dst_pkgconfig_dir, '.'), "pkgconfig")

    return False

def MAIN_CLEAN_BUILD(args):
    set_global(args)

    return False

def MAIN(args):
    set_global(args)

