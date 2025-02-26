import React, { useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import "../QuestionPage/Question.css";

const QuestionPage: React.FC = () => {
  // フォームの状態を管理するstate
  const [formData, setFormData] = useState({
    age: "",
    business: "",
    gender: "",
    comment: "",
  });

  const [submitted, setSubmitted] = useState(false);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  const options = ["男性", "女性", "その他"];

  // 入力変更時の処理
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    // 入力時にエラーメッセージをクリア
    setErrors((prev) => ({
      ...prev,
      [name]: "",
    }));
  };

  // 送信時の処理（バリデーションチェック）
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const newErrors: { [key: string]: string } = {};
    if (!formData.age) newErrors.age = "年齢を入力してください";
    if (!formData.business) newErrors.business = "職業を入力してください";
    if (!formData.gender) newErrors.gender = "性別を選択してください";
    if (!formData.comment) newErrors.comment = "閲覧したい記事について入力してください";

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    const sendData = {
      age: parseInt(formData.age, 10),
      business: formData.business,
      gender: formData.gender,
      comment: formData.comment,
    };

    console.log("送信データ:", sendData);
    setErrors({});
    setSubmitted(true);
  };

  return (
    <section className="background">
      <div className="container px-5 my-5">
        <div className="text-center mb-5">
          <h1 className="fw-bolder">アンケート</h1>
          <p className="lead mb-0">閲覧したい記事についてはできる限り詳しく回答してください</p>
        </div>

        <div className="row gx-5 justify-content-center">
          <div className="col-lg-6">
            {!submitted ? (
              <form onSubmit={handleSubmit}>
                {/* 年齢入力 */}
                <div className="form-floating mb-4">
                  <input
                    className="form-control"
                    id="age"
                    type="number"
                    name="age"
                    value={formData.age}
                    onChange={handleChange}
                  />
                  <label htmlFor="age">年齢</label>
                  {errors.age && <p className="text-danger">{errors.age}</p>}
                </div>

                {/* 職業入力 */}
                <div className="form-floating mb-4">
                  <input
                    className="form-control"
                    id="business"
                    type="text"
                    name="business"
                    value={formData.business}
                    onChange={handleChange}
                  />
                  <label htmlFor="business">職業</label>
                  {errors.business && <p className="text-danger">{errors.business}</p>}
                </div>

                {/* 性別（ラジオボタン） */}
                <div className="mb-4">
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
                  {errors.gender && <p className="text-danger">{errors.gender}</p>}
                </div>

                {/* 閲覧したい記事について */}
                <div className="form-floating mb-3">
                  <textarea
                    className="form-control"
                    id="comment"
                    name="comment"
                    style={{ height: "10rem" }}
                    value={formData.comment}
                    onChange={handleChange}
                  />
                  <label htmlFor="comment">閲覧したい記事について</label>
                  {errors.comment && <p className="text-danger">{errors.comment}</p>}
                </div>

                {/* 送信ボタン */}
                <div className="d-grid">
                  <button className="btn btn-primary btn-lg" type="submit">
                    送信
                  </button>
                </div>
              </form>
            ) : (
              <div className="text-center mt-4">
                <h4>送信ありがとうございました！</h4>
                <p><strong>年齢:</strong> {formData.age}</p>
                <p><strong>職業:</strong> {formData.business}</p>
                <p><strong>性別:</strong> {formData.gender}</p>
                <p><strong>閲覧したい記事について:</strong> {formData.comment}</p>
                <button className="btn btn-secondary mt-3" onClick={() => setSubmitted(false)}>
                  再入力
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};

export default QuestionPage;