clear all
%close all
%% loading data to be read
[file,path] = uigetfile('*.txt');
try
    data = dlmread(file, '\t');
catch
    data = dlmread(file, ',');
end
emg = data (:,2);
markers=data(:,end)*1E-5;
EEG=emg*1E-6;
% filltering data
apass= bandpass(EEG,[8 13], 200);
bpass= bandpass(EEG,[13 32], 200); 
l=length(emg); % lenth of data
t=(0:l-1)*1/200; %calcuating time
%% plots
close all
tiledlayout(2,2)
nexttile
hold on
plot(t,EEG);
plot(t,markers);
title('EEG raw Data');
xlabel('time (s)');
ylabel('EEG Amplitude (uV)');
legend("EEG","Marker");
hold off
nexttile
hold on
plot(t,apass,'r');
title('EEG Alpha Data');
plot(t,markers);
xlabel('time (s)');
ylabel('EEG Amplitude (uV)');
hold off
nexttile
hold on
plot(t,apass,'r');
plot(t,bpass,'c');
plot(t,markers);
title('EEG Beta Data');
xlabel('time (s)');
ylabel('EEG Amplitude (uV)');
hold off
%Frequency plot
fs = 200;
EEG_fft = fft(EEG);
L = length(EEG_fft);
f = (0:L-1)*fs/L;
nexttile
plot(f,abs(EEG_fft));
xlabel('Frequency (Hz)')
ylabel('Amplitude')
title('Frequency Data')


