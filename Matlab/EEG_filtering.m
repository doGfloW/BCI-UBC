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
l=length(emg); % finging lenth of data
t=(0:l-1)*1/200; %calcuating time
%emg_rms=rms(emg); % calcuated the total RMS of the input
%rmsv = sqrt(movmean(emg.^2, 5000)); % clacuast the rms every 5 seconds
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
plot(t,apass,'r');
title('EEG Alpha Data');
xlabel('time (s)');
ylabel('EEG Amplitude (uV)');
nexttile
plot(t,bpass,'c');
title('EEG Beta Data');
xlabel('time (s)');
ylabel('EEG Amplitude (uV)');
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
%% Bandpower
[pks,locs]=findpeaks(data(:,15));
marker=[locs,pks];
a_fft= fft(apass);
l=length(pks);
c=1;
T1=zeros(20,1);
T2=zeros(20,1);
event=zeros(20,1);
for count =1 : length(pks)
    if pks(count)<=2
        T1(c)=locs(count);
        event(c)=1;
        if pks(count)==2
            event(c)=2;
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
event=nonzeros(event);
M=[T1,T2]; 
abandpower=zeros(20,1);
bbandpower=zeros(20,1);
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
bp=[abandpower,bbandpower,r,event];
figure
bar(r)
xlabel('event')
ylabel('|R|')
%% write bandpower into file
wfilename="bandpower_"+file;
writematrix(bp,wfilename,'Delimiter',',')  

%% Consentration
%f = fs*(0:(10000/2))/10000;
% Y = fft(pass);
% P2 = abs(Y/10000);
% P1 = P2(1:10000/2+1);
% P1(2:end-1) = 2*P1(2:end-1);
% 
% plot(f,P1) 
% title('Single-Sided Amplitude Spectrum of S(t)')
% xlabel('f (Hz)')
% ylabel('|P1(f)|')
% disp("done")

