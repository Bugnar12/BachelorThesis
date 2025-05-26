export interface QuizAttempt {
  id: number;
  attempt_no: number;
  score: number;
  total: number;
  timestamp: string;
  questions: {
    text: string;
    userAnswer: string;
    correctAnswer: string;
  }[];
}
