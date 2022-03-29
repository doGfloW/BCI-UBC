clear all
close all
alldata=[];
myDir = uigetdir
myFiles = dir(fullfile(myDir,'*.txt')); %gets all txt files in struct
for k = 1:length(myFiles)
    baseFileName = myFiles(k).name;
    fullFileName = fullfile(myDir, baseFileName);
    try
        data = dlmread(fullFileName, '\t');
    catch
        data = dlmread(fullFileName, ',');
    end
    r_channel= [];
    fprintf(1, 'Now reading %s\n', fullFileName);
    markers=data(:,end)*1E-5;
    [data_row,data_col]=size(data);

     if data_col == 24
        last_channel = 9; % cyton
    else
        last_channel = data_col-2; % ganglion
     end

    for channel=2:(data_col-2)
        EEG = data(:,channel);

        if channel>2 & last_channel==9
            EEG=EEG-(data(:,last_channel)*1E-6);
        end
        
        if sum(EEG)==0
            continue
        end
        fprintf('Now reading channel %d\n', (channel-1));
        apass= bandpass(EEG,[8 13], 200);
        bpass= bandpass(EEG,[13 32], 200);
        [pks,locs]=findpeaks(data(:,15));
        marker=[locs,pks];
        a_fft= fft(apass);
        l=length(pks);
        c=1;
        T1=zeros(200,1);
        T2=zeros(200,1);
        %event={};
        for count =1 : length(pks)
            if pks(count)<=2
                T1(c)=locs(count);
                event(c,1)=1;
                if pks(count)==2
                    event(c,1)=0;
                end
                c=c+1;
            end
        end
        c=1;
        for count =1 : length(pks)
            if pks(count)>10
                T2(c)=locs(count);
                c=c+1;
            end
        end
        T1=nonzeros(T1);
        T2=nonzeros(T2);
        %event=nonzeros(event);
        M=[T1,T2]; 
        abandpower=zeros(20,1);
        bbandpower=zeros(20,1);
        a=zeros(1,20);
        b=zeros(1,20);
        for k = 1:length(M) % indices
            if M(k)==0
                break
            end
            i=M(k,1);
            j=M(k,2);
            a(k)=rms(apass(i:j));
            b(k)=rms(bpass(i:j));
            %bbandpower(k)=bandpower(bpass(i:j));
            %r(k)=abandpower(k)/bbandpower(k);
        end
%         abandpower=nonzeros(abandpower);
%         bbandpower=nonzeros(bbandpower);
         a=nonzeros(a);
         b=nonzeros(b);
        temp=r_channel;
        r_channel=[temp,a,b];
    end
    bp=[r_channel,event];
%     
alldata=[alldata;bp];
end
dataset_folder=cd
dataset_folder=fullfile(dataset_folder,"BCI-UBC","Datasets");
wfilename="RMS_testdataset.xlsx";
dataset_folder=fullfile(dataset_folder,wfilename);
if isfile(dataset_folder)
 fprintf("Dataset Found now adding to data set %s\n",dataset_folder)
else
 %cols_name={}
 xlswrite(dataset_folder,{1,2,3,4,5,6,7,8,9})
 fprintf('Created new dataset called %s\n',dataset_folder)
end
read_data=table2array(readtable(dataset_folder));
write_data=[read_data; alldata];
writematrix(write_data,dataset_folder);
fprintf('done')