import React, { useState, useEffect } from "react";

const SummarySpeech: React.FC = () => {
    const [text, setText] = useState<string>("");
    const [rate, setRate] = useState<number>(1.5); // 内部的な実際の再生速度
    const [isPlaying, setIsPlaying] = useState<boolean>(false);
    const synth = window.speechSynthesis;

    // `public/sample.txt` からテキストを取得
    useEffect(() => {
        fetch("/sample.txt")
            .then((response) => response.text())
            .then((data) => setText(data))
            .catch((error) => console.error("テキストの読み込みに失敗:", error));
    }, []);

    // 再生・停止の切り替え
    const toggleSpeech = () => {
        if (isPlaying) {
            stopSpeech();
        } else {
            startSpeech();
        }
    };

    // 音声再生
    const startSpeech = () => {
        if (!text) return;

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = "ja-JP";
        utterance.rate = rate;
        utterance.onend = () => setIsPlaying(false);
        utterance.onerror = () => setIsPlaying(false);

        synth.speak(utterance);
        setIsPlaying(true);
    };

    // 停止機能（停止後は最初から再生）
    const stopSpeech = () => {
        synth.cancel();
        setIsPlaying(false);
    };

    // 倍速変更（表示倍率と実際の再生倍率を変換）
    const rateMapping: { [key: string]: number } = {
        "0.25x": 0.375,
        "0.5x": 0.75,
        "1.0x": 1.5,  // 実際の 1.5x を "1.0x" として表示
        "1.5x": 2.25,
        "2.0x": 3.0,
    };

    const changeRate = (displayRate: string) => {
        setRate(rateMapping[displayRate]);
    };

    return (
        <div style={{ textAlign: "center", padding: "20px" }}>
            <h2>テキストファイルを読み上げ</h2>
            <div style={{ width: "80%", margin: "0 auto", textAlign: "left", padding: "10px", border: "1px solid gray" }}>
                <p>{text || "テキストを読み込み中..."}</p>
            </div>
            <div>
                <button onClick={toggleSpeech} style={{ margin: "10px" }} disabled={!text}>
                    {isPlaying ? "停止" : "再生"}
                </button>
            </div>
            <div>
                <span>再生速度: {Object.keys(rateMapping).find(key => rateMapping[key] === rate)}</span>
                {Object.keys(rateMapping).map((displayRate) => (
                    <button key={displayRate} onClick={() => changeRate(displayRate)} style={{ margin: "5px" }}>
                        {displayRate}
                    </button>
                ))}
            </div>
        </div>
    );
};

export default SummarySpeech;
