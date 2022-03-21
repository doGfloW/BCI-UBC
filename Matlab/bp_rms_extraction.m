function [bp_values, rms_values] = bp_rms_extraction(data_file)
    % read data from text file
    try
        data = dlmread(convertCharsToStrings(data_file), '\t');
    catch
        data = dlmread(convertCharsToStrings(data_file), ',');
    end

    % define the data size and the output array
    [~, data_col] = size(data);
    alldata = [];
    bp_values = [];
    rms_values = [];

    % loop through each channel in the data
    for channel = 2:(data_col-2)
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

