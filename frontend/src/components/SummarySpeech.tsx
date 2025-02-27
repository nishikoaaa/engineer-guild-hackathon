import React, { useState, useEffect } from "react";

const SummarySpeech: React.FC = () => {
    const [text, setText] = useState<string>("");
    const [rate, setRate] = useState<number>(1.5); // 1.5倍を1.0倍として扱う
    const [isPlaying, setIsPlaying] = useState<boolean>(false);
    const [currentCharIndex, setCurrentCharIndex] = useState<number>(0);
    const [pendingRateChange, setPendingRateChange] = useState<boolean>(false);
    const synth = window.speechSynthesis;
    let utterance: SpeechSynthesisUtterance | null = null;

    // `public/sample.txt` からテキストを取得
    useEffect(() => {
        fetch("/sample.txt")
            .then((response) => response.text())
            .then((data) => setText(data))
            .catch((error) => console.error("テキストの読み込みに失敗:", error));
    }, []);

    // **再生**
    const startSpeech = (resumeFromIndex = 0) => {
        if (!text) return;

        synth.cancel();

        setTimeout(() => {
            utterance = new SpeechSynthesisUtterance(text.slice(resumeFromIndex));
            utterance.lang = "ja-JP";
            utterance.rate = rate;

            utterance.onboundary = (event) => {
                setCurrentCharIndex(resumeFromIndex + event.charIndex);
            };

            utterance.onend = () => {
                setIsPlaying(false);
                setCurrentCharIndex(0);
            };

            utterance.onerror = () => setIsPlaying(false);

            synth.speak(utterance);
            setIsPlaying(true);
        }, 200);
    };

    // **停止**
    const stopSpeech = () => {
        synth.cancel();
        setIsPlaying(false);
    };

    // **はじめから**
    const restartSpeech = () => {
        synth.cancel();
        setCurrentCharIndex(0);
        startSpeech(0);
    };

    // **速度変更（途中から再開）**
    const changeRate = (displayRate: string) => {
        const newRate = rateMapping[displayRate];

        stopSpeech();
        setRate(newRate);
        setPendingRateChange(true);
    };

    // **`rate` の変更を監視し、変更完了後に自動で再生**
    useEffect(() => {
        if (pendingRateChange) {
            setPendingRateChange(false);
            startSpeech(currentCharIndex);
        }
    }, [rate]);

    // **速度マッピング（1.5倍を「1.0倍」として扱う）**
    const rateMapping: { [key: string]: number } = {
        "1.0x": 1.5,
        "1.25x": 1.75,
        "1.5x": 2.0,
        "1.75x": 2.25,
        "2.0x": 2.5,
    };

    return (
        <div style={{ textAlign: "center", padding: "20px" }}>
            <h2>テキストファイルを読み上げ</h2>
            <div style={{ width: "80%", margin: "0 auto", textAlign: "left", padding: "10px", border: "1px solid gray" }}>
                <p>{text || "テキストを読み込み中..."}</p>
            </div>
            <div>
                <button onClick={() => (isPlaying ? stopSpeech() : startSpeech(currentCharIndex))} style={{ margin: "10px" }} disabled={!text}>
                    {isPlaying ? "停止" : "再生"}
                </button>
                <button onClick={restartSpeech} style={{ margin: "10px" }} disabled={!text}>
                    はじめから
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
