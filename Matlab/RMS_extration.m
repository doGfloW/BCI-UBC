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
    markers=data(:,end);
    [data_row,data_col]=size(data);

     if data_col == 24
        last_channel = 9; % cyton
    else
        last_channel = data_col-2; % ganglion
     end

    for channel=2:(last_channel)
        EEG = data(:,channel);
        % refrecencing to channel 8
%         if channel==3 ||channel==4 || channel==5 || channel==7  || channel==8 && last_channel==9
%             EEG=EEG-(data(:,last_channel));
%  
%         end
        %fprintf('Now reading channel %d\n', (channel-1));
        apass= bandpass(EEG,[8 13], 250);
        bpass= bandpass(EEG,[13 32], 250);
        [pks,locs]=findpeaks(data(:,end));
        markers=[locs,pks];
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
            r(k)=a(k)/b(k);
            %bbandpower(k)=bandpower(bpass(i:j));
            %r(k)=abandpower(k)/bbandpower(k);
        end
%         abandpower=nonzeros(abandpower);
%         bbandpower=nonzeros(bbandpower);
         r=nonzeros(a);
         %b=nonzeros(b);
        temp=r_channel;
        r_channel=[temp,r];
    end
    bp=[r_channel,event];
%     
alldata=[alldata;bp];
end
dataset_folder=cd
dataset_folder=fullfile(dataset_folder,"BCI-UBC","Datasets");
wfilename="RMS_newv2.xlsx";
dataset_folder=fullfile(dataset_folder,wfilename);
if isfile(dataset_folder)
    fprintf("Dataset Found now adding to data set %s\n",dataset_folder)
    read_data=table2array(readtable(dataset_folder));
    write_data=[read_data; alldata];
    writematrix(write_data,dataset_folder);
else
    writematrix(alldata,dataset_folder);
    fprintf('Created new dataset called %s\n',dataset_folder)
end

fprintf('done')