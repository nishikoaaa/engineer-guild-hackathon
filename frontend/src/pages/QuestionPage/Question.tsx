import React, { useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css";

const QuestionPage: React.FC = () => {
  const [formData, setFormData] = useState({
    name: "",
    age: "",
    satisfaction: "3", // デフォルト値
    comment: "",
  });

  const [submitted, setSubmitted] = useState(false);

  // 入力変更時の処理
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // 送信時の処理
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
  };

  return (
    <div className="container mt-5">
      <h2 className="mb-4">アンケートフォーム</h2>

      {!submitted ? (
        <form onSubmit={handleSubmit}>
          {/* 名前入力 */}
          <div className="mb-3">
            <label className="form-label">名前</label>
            <input
              type="text"
              className="form-control"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
            />
          </div>

          {/* 年齢入力 */}
          <div className="mb-3">
            <label className="form-label">年齢</label>
            <input
              type="number"
              className="form-control"
              name="age"
              value={formData.age}
              onChange={handleChange}
              required
            />
          </div>

          {/* 満足度（ラジオボタン） */}
          <div className="mb-3">
            <label className="form-label">満足度（1〜5）</label>
            <div>
              {[1, 2, 3, 4, 5].map((num) => (
                <label key={num} className="me-3">
                  <input
                    type="radio"
                    name="satisfaction"
                    value={num.toString()}
                    checked={formData.satisfaction === num.toString()}
                    onChange={handleChange}
                  />{" "}
                  {num}
                </label>
              ))}
            </div>
          </div>

          {/* コメント */}
          <div className="mb-3">
            <label className="form-label">コメント</label>
            <textarea
              className="form-control"
              name="comment"
              value={formData.comment}
              onChange={handleChange}
            />
          </div>

          {/* 送信ボタン */}
          <button type="submit" className="btn btn-primary">
            送信
          </button>
        </form>
      ) : (
        // 送信後の表示
        <div className="mt-4">
          <h4>送信ありがとうございました！</h4>
          <p><strong>名前:</strong> {formData.name}</p>
          <p><strong>年齢:</strong> {formData.age}</p>
          <p><strong>満足度:</strong> {formData.satisfaction}</p>
          <p><strong>コメント:</strong> {formData.comment || "なし"}</p>
          <button className="btn btn-secondary mt-3" onClick={() => setSubmitted(false)}>
            再入力
          </button>
        </div>
      )}
    </div>
  );
};

export default QuestionPage;