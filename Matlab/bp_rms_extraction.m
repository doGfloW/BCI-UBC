function [rms_class, bp_values, rms_values] = bp_rms_extraction(input_data)
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
    else
        last_channel = data_col-2; % ganglion
    end

    % loop through each channel in the data
    for channel = 2:(last_channel)
        % store data for the current channel
        eeg_channel_data = data(:,channel);

        % check if the channel was unconnected (sum of zero means no data)
        if sum(eeg_channel_data) == 0
            continue
        end

        % pass channel data through a bandpass filter
        alpha_bandpass = bandpass(eeg_channel_data, [8 13], 200);
        beta_bandpass = bandpass(eeg_channel_data, [13 32], 200);

        % get bandpower and rms values
        alpha_bp = bandpower(alpha_bandpass);
        beta_bp = bandpower(beta_bandpass);
        alpha_rms = rms(alpha_bandpass);
        beta_rms = rms(beta_bandpass);

        % find peaks of the filtered data
        % [peaks, locs]=findpeaks(data(:, 15));

        % append values to the outputs
        bp_values(end+1) = alpha_bp/beta_bp;
        rms_values(end+1) = alpha_rms;
        rms_values(end+1) = beta_rms;
        
    end
    [rms_class] = RMS_classification(rms_values)
end

