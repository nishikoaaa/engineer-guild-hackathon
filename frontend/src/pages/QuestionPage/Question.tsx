import React, { useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css";

const QuestionPage: React.FC = () => {
  const [formData, setFormData] = useState({
    business: "",
    age: "",
    gender: "",
    comment: "",
  });

  const options = ["男性", "女性", "その他"];
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState("");

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
    if (!formData.gender) {
        setError("性別を選択してください");
        return;
    }
    setError("");
    setSubmitted(true);
  };

  return (
    <div className="container mt-5">
      <h1 className="mb-4">アンケート</h1>
      <h4 className="mb-4">閲覧したい記事についてはできるだけ詳しく回答してください</h4>

      {!submitted ? (
        <form onSubmit={handleSubmit}>
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

          {/* 職業入力 */}
          <div className="mb-3">
            <label className="form-label">職業</label>
            <input
              type="text"
              className="form-control"
              name="name"
              value={formData.business}
              onChange={handleChange}
              required
            />
          </div>

          {/* 性別（ラジオボタン） */}
          <div className="mb-3">
            <label className="form-label">性別</label>
            <div>
              {options.map((option) => (
                <label key={option} className="me-3">
                  <input
                    type="radio"
                    name="gender"
                    value={option}
                    checked={formData.gender === option}
                    onChange={handleChange}
                  />{" "}
                  {option}
                </label>
              ))}
            </div>
            
          </div>

          {/* 閲覧したい記事について入力 */}
          <div className="mb-3">
            <label className="form-label">閲覧したい記事について</label>
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
          <p><strong>職業:</strong> {formData.business}</p>
          <p><strong>年齢:</strong> {formData.age}</p>
          <p><strong>性別:</strong> {formData.gender}</p>
          <p><strong>閲覧したい記事について:</strong> {formData.comment || "なし"}</p>
          <button className="btn btn-secondary mt-3" onClick={() => setSubmitted(false)}>
            再入力
          </button>
        </div>
      )}
    </div>
  );
};

export default QuestionPage;