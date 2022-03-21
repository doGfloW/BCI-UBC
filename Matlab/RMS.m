function [rms_values] = RMS(data_file)
    % initialize varables and read data file
    alldata = [];
    rms_values = [];
    try
        data = dlmread(convertCharsToStrings(data_file), '\t');
    catch
        data = dlmread(convertCharsToStrings(data_file), ',');
    end

    % passing variable to matrix size
    [data_row, data_col] = size(data);

    for channel = 2:(data_col-2)
        EEG = data(:,channel);

        % checking if the row is empty
        if sum(EEG) == 0
            continue
        end

        % filter for alpha and beta and get rms values
        alpha_rms = rms(bandpass(EEG,[8 13], 200));
        beta_rms = rms(bandpass(EEG,[13 32], 200));

        % append values to the output
        rms_values(end+1) = alpha_rms;
        rms_values(end+1) = beta_rms;
    end
