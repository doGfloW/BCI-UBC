function [out_return] = bandpower_extraction(data_folder, export_folder)
    myDir = convertCharsToStrings(data_folder);
    export_folder = convertCharsToStrings(export_folder);
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
        for channel=2:(data_col-2)
            EEG = data(:,channel)*1E-6;
            if sum(EEG)==0
                continue
            end

            EEG = data(:,channel)*1E-6;
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
                    event(c,1)="movement";
                    if pks(count)==2
                        event(c,1)="still";
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
        wfilename="Alexis_Testing.xlsx";
        output_file=fullfile(export_folder,wfilename);
        if isfile(output_file)
         fprintf("Dataset found, now adding to dataset %s\n",output_file)
        else
         %cols_name={}
         xlswrite(output_file,{1,2,3,4,5})
         fprintf('Created new dataset called %s\n',output_file)
        end
        read_data=table2array(readtable(output_file));
        write_data=[read_data; bp];
        writematrix(write_data,output_file);
    end
    out_return = "Function completed."; % not sure what sort of function output we want?
