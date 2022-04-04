clear all

% read data file
[file,path] = uigetfile('*.txt');
try
    data = dlmread(file, '\t');
catch
    data = dlmread(file, ',');
end

emg = data(:, 3);
markers = data(:, end)*1E-5;
EEG = emg*1E-6 + 8.5*1E-4;

% apply bandpass filter to the data (alpha and beta frequency bands)
apass= bandpass(EEG,[8 13], 250);
bpass= bandpass(EEG,[13 32], 250); 

% get length of data and calculate the time for each row
l = length(emg);
t = (0:l-1)*1/250;

% create plots
close all
tiledlayout(2,2)
nexttile
hold on

% plot raw EEG data
plot(t, EEG);
plot(t, markers);
title('Raw EEG Data');
xlabel('Time (s)');
ylabel('EEG Amplitude (uV)');
legend("EEG", "Marker");
hold off
nexttile
hold on

% plot filtered alpha data
plot(t, apass,'r');
title('EEG Alpha Data');
plot(t, markers);
xlabel('Time (s)');
ylabel('EEG Amplitude (uV)');
legend("Alpha EEG", "Marker");
hold off
nexttile
hold on

% plot filtered alpha and beta data
plot(t, bpass,'c');
plot(t, markers);
title('EEG Beta Data');
xlabel('Time (s)');
ylabel('EEG Amplitude (uV)');
legend("Beta EEG", "Marker");
hold off

% FFT plot
fs = 200;
EEG_fft = fft(EEG);
L = length(EEG_fft);
f = (0:L-1)*fs/L;
nexttile
plot(f, abs(EEG_fft));
xlabel('Frequency (Hz)')
ylabel('Amplitude')
title('FFT Plot')
