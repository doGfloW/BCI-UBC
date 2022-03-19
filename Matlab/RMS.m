function [output] = RMS(data_folder)
    %inissilize varables 
    alldata=[];
    a_channel= [];
    b_channel= [];
    myDir = convertCharsToStrings(data_folder);
    try
        data = dlmread(data_folder, '\t');
    catch
        data = dlmread(data_folder, ',');
    end
    [data_row,data_col]=size(data); % passing variabe to matixe size

    for channel=2:(data_col-2)
        EEG = data(:,channel);
        if sum(EEG)==0 % checking if the row is empty
            continue
        end
        % filtering for alpha and beta
        apass= bandpass(EEG,[8 13], 200);
        bpass= bandpass(EEG,[13 32], 200);
        alpha_rms=zeros(1,20);
        beta_rms=zeros(1,20);

        alpha_rms=rms(apass);
        beta_rms=rms(bpass);

        temp_a=a_channel;
        a_channel=[temp_a,alpha_rms,beta_rms];
     end
    % adds the rms variabel and move to next channel    
    output= a_channel; %returns the feature extreation
    end
