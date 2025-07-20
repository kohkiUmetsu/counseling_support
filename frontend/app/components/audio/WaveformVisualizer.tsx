import React, { useEffect, useRef } from 'react';

interface WaveformVisualizerProps {
  audioStream?: MediaStream;
  isActive: boolean;
  width?: number;
  height?: number;
  barColor?: string;
  backgroundColor?: string;
}

export const WaveformVisualizer: React.FC<WaveformVisualizerProps> = ({
  audioStream,
  isActive,
  width = 300,
  height = 100,
  barColor = '#3B82F6',
  backgroundColor = '#F3F4F6',
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationFrameRef = useRef<number>();
  const analyserRef = useRef<AnalyserNode>();
  const audioContextRef = useRef<AudioContext>();

  useEffect(() => {
    if (!audioStream || !isActive || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const canvasContext = canvas.getContext('2d');
    if (!canvasContext) return;

    audioContextRef.current = new AudioContext();
    analyserRef.current = audioContextRef.current.createAnalyser();
    analyserRef.current.fftSize = 256;

    const source = audioContextRef.current.createMediaStreamSource(audioStream);
    source.connect(analyserRef.current);

    const bufferLength = analyserRef.current.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const draw = () => {
      if (!analyserRef.current || !isActive) return;

      animationFrameRef.current = requestAnimationFrame(draw);
      analyserRef.current.getByteFrequencyData(dataArray);

      canvasContext.fillStyle = backgroundColor;
      canvasContext.fillRect(0, 0, width, height);

      const barWidth = (width / bufferLength) * 2.5;
      let barHeight;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        barHeight = (dataArray[i] / 255) * height;

        canvasContext.fillStyle = barColor;
        canvasContext.fillRect(x, height - barHeight, barWidth, barHeight);

        x += barWidth + 1;
      }
    };

    draw();

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, [audioStream, isActive, width, height, barColor, backgroundColor]);

  useEffect(() => {
    if (!isActive && canvasRef.current) {
      const canvasContext = canvasRef.current.getContext('2d');
      if (canvasContext) {
        canvasContext.fillStyle = backgroundColor;
        canvasContext.fillRect(0, 0, width, height);
      }
    }
  }, [isActive, backgroundColor, width, height]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      className="rounded-lg shadow-inner"
    />
  );
};