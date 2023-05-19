# CleanMyLinux

## How to Deploy:
1) Download clean.deb file on your machine
2) Install this package by command dpkg -i clean.deb
3) Now, installed file should get permition to be executed. I did it by sudo chmod +x /usr/local/bin/clean. But also this command can be just added to 
sudo safe path to be executable with sudo. 
4) After that you can run it simply by writing 'clean' in terminal. You will see 4 options what to do: delete cash, delete old files, delete malwares
(we used  clamscan for this), boost system(different methods, including killing zombie processes). You can run this commands sequentially. Output will be given in
terminal.
5) To finish the program you can simlpy use Ctrl+C. Interrupt is handled by program.
