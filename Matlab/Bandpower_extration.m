clear all
close all
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
    markers=data(:,end);
    [data_row,data_col]=size(data);

    if data_col == 24
        last_channel = 9; % cyton
    else
        last_channel = data_col-2; % ganglion
    end
    for channel=2:last_channel

        EEG = data(:,channel)*1E-6;
        if channel==3 ||channel==4 || channel==5 || channel==7  || channel==8 && last_channel==9
            EEG=EEG-(data(:,last_channel)*1E-6);
        end

        apass= bandpass(EEG,[8 13], 250);
        bpass= bandpass(EEG,[13 32], 250);
        [pks,locs]=findpeaks(data(:,end));
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
        r=zeros(1,20);
        for k = 1:length(M) % indices
            if M(k)==0
                break
            end
            i=M(k,1);
            j=M(k,2);
            abandpower(k)=bandpower(apass(i:j));
            bbandpower(k)=bandpower(bpass(i:j));
            r(k)=abandpower(k)/bbandpower(k);
        end
        abandpower=nonzeros(abandpower);
        bbandpower=nonzeros(bbandpower);
        r=nonzeros(r);
        temp=r_channel;
        r_channel=[temp,r];   
    end
    bp=[r_channel,event];
    dataset_folder=cd;
    dataset_folder=fullfile(dataset_folder,"BCI-UBC","Datasets");
    wfilename="new_8.xlsx";
    dataset_folder=fullfile(dataset_folder,wfilename);
    if isfile(dataset_folder)
     fprintf("Dataset Found now adding to data set %s\n",dataset_folder)
    else
     %cols_name={}
     xlswrite(dataset_folder,{1,2,3,4,5,6,7,8,9})
     fprintf('Created new dataset called %s\n',dataset_folder)
    end
    read_data=table2array(readtable(dataset_folder));
    write_data=[read_data; bp];
    writematrix(write_data,dataset_folder); 
end
fprintf('done')