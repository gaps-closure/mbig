#!/usr/bin/env python3
"""
    Fetch the libraries form an ubuntu/debian distribution to build against
    Used for cross compiling to sepate OS installs, and non-local machines
    matching the GAPS enviroemnt
    
    By default we fetch the eoan distribution for the specified architecture
    
    Supported architectures:
        amd64 (x86_64)
        i386  (x86_32)
        arm64 (aarch64)
        armhf (arm32)
        
    run with --help for full usage details
"""

import argparse
import subprocess
import shutil
import os.path
import os
import re

#libraries/dev headers required for building the system
BOOTSTRAP_INCLUDE = "libconfig-dev,libconfig9,libunwind8,libunwind-dev," \
    "libsodium23,libsodium-dev,liblzma5,liblzma-dev,libc6-dev,libzmq3-dev"

#as we will remove all but /usr/include and /usr/lib we do not need every package
#so exclude some larger ones
BOOTSTRAP_EXCLUDE = "gcc-9-base,e2fsprogs,fdisk"

def bootstrap_dirname(suite, arch):
    """From the suite/arch calculate the directory name to extract debootstrap into"""
    return "./" + suite + "-" + arch
    
def call_debootstrap(suite, arch, mirror):
    """Call a fakeroot debootstrap to fetch relivante packages"""
    
    args = [
        "fakeroot",
        "fakechroot",
        "debootstrap",
        "--foreign",
        "--no-resolve-deps",
        "--variant=minbase",
        "--components=main,restricted,universe,multiverse",
        "--arch=" + arch,
        "--include",
        BOOTSTRAP_INCLUDE,
        "--exclude",
        BOOTSTRAP_EXCLUDE,
        suite,
        bootstrap_dirname(suite, arch),
        mirror
    ]
    return(subprocess.run(args).returncode == 0) 

def cleanup(suite,arch):
    """Cleanup the debootstrap directory"""
    bsdir = bootstrap_dirname(suite, arch)
    if(os.path.isdir(bsdir)):
        print("removing " + bsdir)
        shutil.rmtree(bsdir,ignore_errors=True)
        
def remove_libs(suite,arch):
    """Remove the libs/incudes directory for the architecture"""
    includes_dir = arch+"-includes"
    libs_dir = arch+"-libs"
    
    if(os.path.isdir(includes_dir)):
        print("remove " + includes_dir)
        shutil.rmtree(includes_dir,ignore_errors=True)
        
    if(os.path.isdir(libs_dir)):
        print("remove " + libs_dir)
        shutil.rmtree(libs_dir,ignore_errors=True)

def extract_package_files(packagefile):
    """Extract the data tar from a specific package into the debootstrap directory
       this logic expect we are in a temp directory with the deb file one directory
       under the debootstrap directory.
    """    
    
    #deb packages are in an "ar" archive that contains a control + data tars
    #and a debian meta data file, we simply extract the data tar ignoring the rest
    old_cwd = os.getcwd()
    try:
        args=[
            "ar",
            "x",
            packagefile]
        if(subprocess.run(args).returncode == 0):
            print("extract data from " + packagefile)
            os.chdir("..")
            args=[
                "tar",
                "-xJvf",
                os.path.join(old_cwd,"data.tar.xz")
            ]
            if(subprocess.run(args).returncode == 0):
                print("Done extracting " + packagefile)
            else:
                print("unexpected error extracting tar.xz for " + packagefile)
        else:
            print("unable to extract " + packagefile)
    finally:
        os.chdir(old_cwd)
    
def extract_packages(suite,arch):
    """debootstrap first pass dosn't extract all the deb packages,
       here we extract all packages from BOOTSTRAP_INCLUDE into the
       output directory
    """
    packagelst = BOOTSTRAP_INCLUDE.split(",")
    
    old_cwd = os.getcwd()
    tmpdir = os.path.join(bootstrap_dirname(suite, arch),"pkg-tmp")
    os.mkdir(tmpdir)
    try:
        os.chdir(tmpdir)
        packagecache = os.path.join("..",
                       "var","cache","apt","archives")
        
        for deb in os.listdir(packagecache):
            if(not deb.endswith(".deb")):
                continue
            for p in packagelst:
                if(deb.startswith(p)):
                    print("Extract " + deb)
                    extract_package_files(os.path.join(packagecache,deb))
            
    finally:
        os.chdir(old_cwd)
        
def fix_links(suite,arch):
    """Some packages provide shared library symlinks with the full qualified domain, convert them to local links
       (as otherwise the link will not match our build enviroment)
    """
    libs_dir = arch+"-libs"
    tree = os.walk(os.path.join(libs_dir))
    for (path,dirs,files) in tree:
        for file in files:
            
            filepath = os.path.join(path,file)
            print(filepath)
            if(os.path.islink(filepath)):
                linkpath = os.readlink(filepath)
                if(linkpath.startswith("/")):
                    print("Found absolute symlink: %s->%s"%(filepath,linkpath))
                    linkfile = os.path.basename(linkpath)
                    if(os.path.exists(os.path.join(path,linkfile))):
                        print("Fix symlink")
                        os.unlink(filepath)
                        os.symlink(linkfile,filepath)

def fix_libc(suite,arch):
    """Fix the libc LD script to not use full paths"""
    libs_dir = arch+"-libs"
    groupline = re.compile(r'GROUP.*(libc\.so(?:\.\d+)).*(libc.*?\.a).*(ld-linux.*?.so(?:\.\d+))')
    
    tree = os.walk(os.path.join(libs_dir))
    for (path,dirs,files) in tree:
        for file in files:
            if(file == "libc.so"):
                filepath = os.path.join(path,file)
                print("Found libc.so [%s] updating check LD script"%(filepath,))
                
                content = ""
                with open(filepath,"r",encoding="utf-8") as fp:
                    for ln in fp:
                        m = groupline.match(ln)
                        if(m is not None):
                            ln = "GROUP ( %s %s AS_NEEDED ( %s ) )\n" % (
                                m.group(1),
                                m.group(2),
                                m.group(3)
                            )
                            print("Update Group line:\n" + ln)
                        content += ln
                with open(filepath,"w",encoding="utf-8") as fp:
                    fp.write(content)
                

def move_libs(suite,arch):
    """Move all the libs/includes to the output location"""
    includes_dir = arch+"-includes"
    libs_dir = arch+"-libs"
    bootstrap_dir = bootstrap_dirname(suite,arch)
    
    src_includes = os.path.join(bootstrap_dir,"usr","include")
    src_libs = os.path.join(bootstrap_dir,"usr","lib")
    
    print("Move [%s] to [%s]"%(src_includes, includes_dir))
    shutil.move(src_includes, includes_dir)
    print("Move [%s] to [%s]"%(src_libs, libs_dir))
    shutil.move(src_libs, libs_dir)
    
    cleanup(suite,arch)
    
def main():
    """Main entry point"""
    
    #configure/parse command line
    parser = argparse.ArgumentParser()
    parser.add_argument("arch", choices=("amd64", "i386", "arm64", "armhf"),
                help="Architecture to fetch libraries for")
    parser.add_argument("-u","--url",type=str, default="",
                help="Override ubuntu/debian package mirror, defaults for ubuntu will be used if left blank")
    parser.add_argument("-s","--suite",type=str, default="eoan",
                help="The distribution's suite, default is 'eoan'")
    args = parser.parse_args()
    
    if(args.url == ""):
        #if no url is provided determine the mirror url here
        if(args.arch in ("amd64", "i386")):
            args.url = "http://archive.ubuntu.com/ubuntu/"
        else:
            args.url = "http://ports.ubuntu.com/ubuntu-ports/"
    
    #cleanup any previous install of this architecture
    cleanup(args.suite, args.arch)
    print("install [%s] for [%s] using mirror [%s]"%(args.suite, args.arch, args.url))
    if(call_debootstrap(args.suite, args.arch, args.url)):
        print("Succeess")
    else:
        print("Fail.. cleanup")
        cleanup(args.suite, args.arch)
        return
    
    print("Extracted downloaded packages")
    extract_packages(args.suite, args.arch)
    
    print("Move libs/includes into final location")
    remove_libs(args.suite, args.arch)
    move_libs(args.suite, args.arch)
    fix_links(args.suite, args.arch)
    fix_libc(args.suite, args.arch)
    
    print("")
    print("Done!")
    
if __name__ == "__main__":
    main()
