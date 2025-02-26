import React, { useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css";

const QuestionPage: React.FC = () => {
  const [formData, setFormData] = useState({
    age: "",
    job: "",
    gender: "",
    comment: "",
  });

  const [submitted, setSubmitted] = useState(false);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [loading, setLoading] = useState(false);

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
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const newErrors: { [key: string]: string } = {};
    if (!formData.age) newErrors.age = "年齢を入力してください";
    if (!formData.job) newErrors.job = "職業を入力してください";
    if (!formData.gender) newErrors.gender = "性別を選択してください";
    if (!formData.comment) newErrors.comment = "閲覧したい記事について入力してください";

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setLoading(true);

    const sendData = {
      userid: 0,  // バックエンド側で current_user に置き換えられるのでダミー
      age: parseInt(formData.age, 10),
      gender: formData.gender,
      job: formData.job,
      preferred_article_detail: formData.comment,
    };

    console.log("送信データ:", sendData);

    try {
      const response = await fetch("http://localhost:4000/regist_survey", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include", // Cookie を含める (認証済みユーザーの情報を送る)
        body: JSON.stringify(sendData),
      });

      if (response.ok) {
        // 挿入が完了したら TopPage にリダイレクト
        window.location.href = "http://localhost:3000/TopPage";
      } else {
        const data = await response.json();
        console.error("送信エラー:", data.detail);
        setErrors({ general: "アンケートの送信に失敗しました" });
      }
    } catch (error: any) {
      console.error("通信エラー:", error);
      setErrors({ general: "サーバーに接続できませんでした" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <section
      className="background"
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "linear-gradient(135deg, #4b6cb7 0%, #182848 100%)",
        color: "#fff",
        textAlign: "center",
        padding: "2rem",
      }}
    >
      <div className="container px-5 my-5">
        <div className="text-center mb-5">
          <h1 className="fw-bolder">アンケート</h1>
          <p className="lead mb-0">
            閲覧したい記事についてはできる限り詳しく回答してください
          </p>
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
                    id="job"
                    type="text"
                    name="job"
                    value={formData.job}
                    onChange={handleChange}
                  />
                  <label htmlFor="job">職業</label>
                  {errors.job && <p className="text-danger">{errors.job}</p>}
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
                <p>
                  <strong>年齢:</strong> {formData.age}
                </p>
                <p>
                  <strong>職業:</strong> {formData.job}
                </p>
                <p>
                  <strong>性別:</strong> {formData.gender}
                </p>
                <p>
                  <strong>閲覧したい記事について:</strong> {formData.comment}
                </p>
                <button
                  className="btn btn-secondary mt-3"
                  onClick={() => setSubmitted(false)}
                >
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