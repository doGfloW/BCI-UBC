function [bp_class,rms_class, bp_values, rms_values] = bp_rms_extraction(input_data)
    % check if the data is character/string or 2D numerical array
    % if ischar(input_data) | isstring(input_data)
    %     % read data from text file
    %     try
    %         data = dlmread(convertCharsToStrings(input_data), '\t');
    %     catch
    %         data = dlmread(convertCharsToStrings(input_data), ',');
    %     end
    % else
    %     % assign the data to a variable
    %     data = input_data
    % end

    try
        data = dlmread(convertCharsToStrings(input_data), '\t');
    catch
        data = dlmread(convertCharsToStrings(input_data), ',');
    end

    % define the data size and the output array
    [~, data_col] = size(data);
    alldata = [];
    bp_values = [];
    rms_values = [];

    if data_col == 24
        last_channel = 9; % cyton
        f=250;
    else
        last_channel = data_col-2; % ganglion
        f=200;
    end

    % loop through each channel in the data
    for channel = 2:(last_channel)
        % store data for the current channel
        eeg_channel_data = data(:,channel)*1E-6;
         if channel==3 ||channel==4 || channel==5 || channel==7  || channel==8 && last_channel==9
            eeg_channel_data=eeg_channel_data-(data(:,last_channel)*1E-6);
        end


        % pass channel data through a bandpass filter
        alpha_bandpass = bandpass(eeg_channel_data, [8 13], f);
        beta_bandpass = bandpass(eeg_channel_data, [13 32], f);

        for x= 1:350
             alpha_bandpass(1,:) = [];
             alpha_bandpass(end,:) = [];
             beta_bandpass(1,:) = [];
             beta_bandpass(end,:) = [];
            x=x+1;
        end
        % get bandpower and rms values
        alpha_bp = bandpower(alpha_bandpass);
        beta_bp = bandpower(beta_bandpass);
        alpha_rms = rms(alpha_bandpass);
        beta_rms = rms(beta_bandpass);
        

        % find peaks of the filtered data
        % [peaks, locs]=findpeaks(data(:, 15));

        % append values to the outputs
        bp_values(end+1) = alpha_bp/beta_bp;
        rms_values(end+1) = alpha_rms/beta_rms;
        
        
    end
    if  last_channel == 9

        [bp_class] = BP_classification_cyton(bp_values);
        [rms_class] = RMS_classification_cyton(rms_values);
    else 
        [bp_class] = BP_classification(bp_values);
        [rms_class] = RMS_classification(rms_values);
    end
end

