======= User Guide =======

0. Please install FileZilla Client at first
   https://filezilla-project.org/download.php?platform=win64 

1. Logging into AMR with user - "pyuser", then delete folder: '/data/etc/extra_preset_cmd', '/data/etc/extra_preset_cmd/extra_ui',
   '/data/etc/extra_preset_cmd/extra_mscript'

2. Upload the case directory and the files inside to AMR with assigned path 
    ✔ IMPORTANT: The directory and necessary files with correct filenames must be matched (other files may be 
                  needed for necessary files, so please upload all files inside with directory) or it will not work.

    extra_preset_cmd: 
    A directory that contains the file "cmd.txt" inside, AMR will load AI parameters inside "cmd.txt" and 
    put them to every moving mission step automatically. Upload directory and all files inside to path '/data/etc' in AMR.

        <extra_preset_cmd>
            └─ cmd.txt 


    extra_ui: 
    A directory that contains the file "main.py" inside, AMR will excute this "main.py" when 'Local Task Manager' is starting,
    its lifetime follows 'Local Task Manager'. Upload directory and all files inside to path '/data/etc' in AMR.

        <extra_ui>
            └─ main.py 

    
    
    extra_mscript: 
    A directory that contains (maybe) a lot of files with ".py" extension inside, AMR can excute this custom 
    mission script (mscript) through mission step - 'MissionScript'. Upload directory and all files inside 
    to path '/data/etc' in AMR. 

        <extra_mscript>
            ├─ any_name_without_space_1.py 
            ├─ any_name_without_space_2.py
            └─ ...

        Mission step usage: 
            ["MissionScript", "any_name_without_space_1", "EXTRA", ["-c","5"]]
                    ^                     ^                   ^          ^   
                   (a)                   (b)                 (c)        (d) 

            (a) Mission step name - "MissionScript"
            (b) The python program's filename but without ".py" extension
            (c) Means the mscript inside '/data/etc/extra_mscript'
            (d) The python program's argument variables if needed.


3. Upload the case name 
    Case name is inside "case.txt", it is necessary for tracking which case is used by AMR now. Upload "case.txt" to
    path '/data/etc' in AMR. "case.txt" is inside the case directory.


4. Upload the eth3.cfg
    "eth3.cfg" contained configuration of extend ethernet network port. Upload this file to 
    '/data/etc/network/interfaces.d' in AMR. "eth3.cfg" is inside the case directory.


5. Set the size:
    Open "size.cfg" and set correct value of size parameters matched. Setting action must through FMS 
    (in "Property Setting" window --> "Size" tab). "size.cfg" is inside the case directory.
    
    
PS. If you found there is something missing in case directory, it may mean that case doesn't need 
    that function or configuration. 



