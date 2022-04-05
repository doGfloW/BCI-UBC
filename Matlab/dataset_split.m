% splits dataset into training and testing
clear all
close all
[file,path] = uigetfile('*.xlsx','*.xlx');
file_location=fullfile(path,file);
data=table2array(readtable(file_location));
[m,n] = size(data) ;
P = 0.80 ;
idx = randperm(m)  ;
Training = data(idx(1:round(P*m)),:) ; 
Testing = data(idx(round(P*m)+1:end),:) ;
writematrix(Training,file_location,'Sheet','Training');
writematrix(Testing,file_location,'Sheet','Testing');
print("done");