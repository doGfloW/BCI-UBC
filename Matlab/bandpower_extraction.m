function [bp_values] = bandpower_extraction(data_file)
    % read data from text file
    try
        data = dlmread(convertCharsToStrings(data_file), '\t');
    catch
        data = dlmread(convertCharsToStrings(data_file), ',');
    end

    % define the data size and the output array
    [data_row, data_col] = size(data);
    bp_values = [];

    % loop through each channel in the data
    for channel = 2:(data_col-2)
        % store data for the current channel
        eeg_channel_data = data(:,channel) * 1E-6;

        % check if the channel was unconnected (sum of zero means no data)
        if sum(eeg_channel_data) == 0
            continue
        end

        % pass channel data through a bandpass filter
        alpha_bandpower = bandpower(bandpass(eeg_channel_data, [8 13], 200));
        beta_bandpower = bandpower(bandpass(eeg_channel_data, [13 32], 200));

        % find peaks of the filtered data
        % [peaks, locs]=findpeaks(data(:, 15));

        % store new values with total output
        bp_values(end+1) = alpha_bandpower/beta_bandpower;
    end
end
