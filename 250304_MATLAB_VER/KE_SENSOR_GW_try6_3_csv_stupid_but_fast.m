clear; clc;

% 시리얼 포트 설정
port = "COM4"; % 아두이노 연결된 포트
baudRate = 1000000; % 아두이노와 동일한 통신 속도
serialObj = serialport(port, baudRate);
configureTerminator(serialObj, "LF"); % 줄바꿈(LF) 기준으로 데이터 읽기
flush(serialObj); % 기존 버퍼 비우기

% 데이터 저장 변수 초기화
bufferSize = 500; % 표시할 데이터 개수
voltageData = zeros(1, bufferSize); % 원본 데이터 저장
filteredData = zeros(1, bufferSize); % 필터링된 데이터 저장
differenceData = zeros(1, bufferSize); % 원본 데이터와 필터링된 데이터의 차이 저장
t = 1:bufferSize; % X축 데이터

% 고역통과 필터 설정
fs = 240; % 샘플링 주파수 (Hz)
highCutoff = 1; % 고역통과 필터 차단 주파수 (Hz)
order = 5; % 필터 차수
[b, a] = butter(order, highCutoff / (fs / 2), 'high'); % 고역통과 필터 계수 계산
filterState = zeros(1, order); % 필터 상태 초기화

% 실시간 플로팅 초기화
figure;
hold on;
rawPlot = plot(t, voltageData, 'Color', [0.7 0.7 0.7], 'DisplayName', 'Raw Data'); % 원본 데이터 (회색)
filteredPlot = plot(t, filteredData, 'r', 'DisplayName', 'High-Pass Filtered'); % 필터링된 데이터 (빨간색)
differencePlot = plot(t, differenceData, 'b', 'DisplayName', 'Difference'); % 원본과 필터 차이 (파란색)
peaksPlot = scatter([], [], 'filled', 'r', 'DisplayName', 'Peaks'); % 피크 표시용 scatter plot
xlabel('Sample');
ylabel('Voltage (V)');
ylim([0, 0.1]); % Y축 범위 조정
legend;
grid on;
title('Real-Time Voltage with High-Pass Filter and Difference Plot');

% 실시간 데이터 수신 및 업데이트 루프
while true
    if serialObj.NumBytesAvailable > 0 % 데이터가 있을 때만 읽기
        data = readline(serialObj); % 한 줄 읽기
        Vout = str2double(data); % 숫자로 변환
        
        if ~isnan(Vout) % 유효한 데이터만 처리
            % 데이터 저장 (FIFO 방식)
            voltageData = [voltageData(2:end), Vout];

            % 필터 적용 (배열 전체가 아니라 새로운 값만 처리)
            [filteredSample, filterState] = filter(b, a, Vout, filterState);
            filteredData = [filteredData(2:end), filteredSample];

            % 원본 데이터와 필터링된 데이터의 차이 계산
            differenceData = [differenceData(2:end), Vout - filteredSample];

            % 그래프 업데이트 (빠른 속도를 위해 'set' 사용)
            rawPlot.YData = voltageData;
            filteredPlot.YData = filteredData;
            differencePlot.YData = differenceData;

            % 차이값에서 피크 찾기 (MinPeakHeight, MinPeakDistance, Threshold 추가)
            [peaks, locs] = findpeaks(differenceData, 'MinPeakHeight', 0.02, 'MinPeakDistance', 10, 'MinPeakProminence', 0.001, 'MaxPeakWidth', 1000); % 피크 찾기

            if ~isempty(peaks) % 피크가 있을 때만 scatter 업데이트
                % scatter로 피크만 표시 (이전 피크는 삭제)
                set(peaksPlot, 'XData', locs, 'YData', peaks);
            end

            % 일정 주기로 그래프 업데이트
            drawnow limitrate; % 그래프 업데이트 속도 제한
        end
    end
end
