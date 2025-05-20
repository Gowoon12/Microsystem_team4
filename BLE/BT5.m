clear; clc;

% Serial port setup
port = "COM7"; 
baudRate = 115200;
serialObj = serialport(port, baudRate);
configureTerminator(serialObj, "LF"); 
flush(serialObj); 

% Initialize data storage variables
bufferSize = 1000;
voltageData = zeros(1, bufferSize); 
filteredData = zeros(1, bufferSize);
t = 1:bufferSize;

% Low-pass filter setup
fs = 240; % Sampling frequency (Hz)
lowCutoff = 5; % Low-pass filter cutoff frequency (Hz)
order = 2; % Filter order
[b, a] = butter(order, lowCutoff / (fs / 2), 'low');
filterState = zeros(order, 1); 

% Real-time plotting initialization
figure;
hold on;
rawPlot = plot(t, voltageData, 'Color', [0.7 0.7 0.7], 'DisplayName', 'Raw Data'); 
filteredPlot = plot(t, filteredData, 'r', 'LineWidth', 2, 'DisplayName', 'Low-Pass Filtered');
peakPlot = plot(NaN, NaN, 'bo', 'MarkerFaceColor', 'b', 'DisplayName', 'Peaks');
dcLine = line([1, bufferSize], [NaN, NaN], 'Color', 'g', 'LineStyle', '--', 'DisplayName', 'DC Value');

xlabel('Sample');
ylabel('Voltage (V)');
ylim([0, 1]);
legend;
grid on;
title('Real-Time Low-Pass Filtering with Peak Size Calculation');

currentPeriodText = text(10, 0.08, 'Current Period: N/A', 'FontSize', 12);
avgPeriodText = text(10, 0.075, 'Average Period: N/A', 'FontSize', 12);
currentPeakText = text(10, 0.07, 'Current Peak Size: N/A', 'FontSize', 12);
avgPeakText = text(10, 0.065, 'Average Peak Size: N/A', 'FontSize', 12);

peakIntervals = [];
peakSizes = [];

statusMapping = containers.Map( ...
    {'OK', 'No Signal', 'Weak Signal', 'Slow Signal'}, ...
    {1, 0, -1, -2} ...
);

csvFileName = 'D:\2025\Paper work\2025_Sensor\BT\sensor_data_4.csv';

header = {'Time', 'Raw Data', 'Filtered Data', 'DC Value', 'Current Period', 'Average Period', 'Current Peak Size', 'Average Peak Size', 'Status'};

if ~isfile(csvFileName)
    writecell(header, csvFileName);
end

bufferForWriting = zeros(100, 9); % 미리 크기 고정 (숫자 배열로)
writeIndex = 1;

% 플롯 업데이트 빈도 설정 (예: 10번마다)
plotUpdateInterval = 10;
plotUpdateCounter = 0;

while true
    if serialObj.NumBytesAvailable > 0
        data = readline(serialObj);
        Vout = str2double(data);

        if ~isnan(Vout)
            % 데이터 갱신
            voltageData = [voltageData(2:end), Vout];
            [filteredSample, filterState] = filter(b, a, Vout, filterState);
            filteredData = [filteredData(2:end), filteredSample];
            
            % DC value 계산
            dcValue = mean(filteredData);
            
            % 피크 검출
            [peaks, locs] = findpeaks(filteredData, 'MinPeakHeight', 0.02, 'MinPeakDistance', 10, 'MinPeakProminence', 0.001);

            % 상태 평가 및 텍스트 업데이트
            status = statusMapping('OK'); % 기본값 OK

            if ~isempty(peaks)
                peakIntervals = [peakIntervals, diff(locs)];
                peakSizes = [peakSizes, abs(peaks - dcValue)];
                currentPeakSize = abs(peaks(end) - dcValue);
                avgPeakSize = mean(peakSizes);

                if ~isempty(peakIntervals)
                    currentPeriod = peakIntervals(end) / fs;
                    avgPeriod = mean(peakIntervals) / fs;
                else
                    currentPeriod = NaN;
                    avgPeriod = NaN;
                end

                if currentPeakSize < 0.005 && currentPeriod > 2
                    status = statusMapping('No Signal');
                elseif currentPeakSize < 0.005
                    status = statusMapping('Weak Signal');
                elseif currentPeriod > 2
                    status = statusMapping('Slow Signal');
                end
            else
                currentPeriod = NaN;
                avgPeriod = NaN;
                currentPeakSize = NaN;
                avgPeakSize = NaN;
                status = statusMapping('No Signal');
            end
            
            % 플롯 갱신 (10번마다 한 번씩만)
            plotUpdateCounter = plotUpdateCounter + 1;
            if plotUpdateCounter >= plotUpdateInterval
                rawPlot.YData = voltageData;
                filteredPlot.YData = filteredData;
                set(dcLine, 'YData', [dcValue dcValue]);
                set(peakPlot, 'XData', locs, 'YData', peaks);
                set(currentPeriodText, 'String', ['Current Period: ', num2str(currentPeriod, '%.4f'), ' s']);
                set(avgPeriodText, 'String', ['Average Period: ', num2str(avgPeriod, '%.4f'), ' s']);
                set(currentPeakText, 'String', ['Current Peak Size: ', num2str(currentPeakSize, '%.4f'), ' V']);
                set(avgPeakText, 'String', ['Average Peak Size: ', num2str(avgPeakSize, '%.4f'), ' V']);
                drawnow limitrate;
                plotUpdateCounter = 0;
            end

            % 데이터 버퍼에 저장 (숫자 배열)
            bufferForWriting(writeIndex, :) = [t(end), Vout, filteredSample, dcValue, currentPeriod, avgPeriod, currentPeakSize, avgPeakSize, status];
            writeIndex = writeIndex + 1;

            % 100개 모이면 한번에 파일 저장
            if writeIndex > 100
                writematrix(bufferForWriting, csvFileName, 'WriteMode', 'append');
                writeIndex = 1;
            end
        end
    end
end
