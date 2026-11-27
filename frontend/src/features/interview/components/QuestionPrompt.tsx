import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useState } from "react";

import { INTERVIEW_TEXTS } from "@/features/interview/texts";
import type { Question } from "@/features/interview/types";

const HEADING_ID = "interview-question";

interface QuestionPromptProps {
  question: Question;
  disabled: boolean;
  onAnswer: (answer: string) => void;
}

/** One question at a time. An option or a typed answer goes to the chat as the next message. */
export function QuestionPrompt({ question, disabled, onAnswer }: QuestionPromptProps): React.JSX.Element {
  const [text, setText] = useState("");
  const answer = text.trim();
  const options = question.options ?? [];
  return (
    <div className="mx-auto flex w-full max-w-2xl flex-col gap-6">
      <div className="flex min-w-0 flex-col gap-4" role="group" aria-labelledby={HEADING_ID}>
        <Typography id={HEADING_ID} variant="h2">
          {question.question}
        </Typography>
        {options.length > 0 ? (
          <div className="flex flex-col gap-2">
            {options.map((option) => (
              <Button
                key={option}
                variant="outlined"
                disabled={disabled}
                onClick={() => onAnswer(option)}
                sx={{ justifyContent: "flex-start", textAlign: "left", py: 1.5 }}
              >
                {option}
              </Button>
            ))}
          </div>
        ) : null}
      </div>
      {question.free_text ? (
        <form
          className="flex flex-col gap-2"
          onSubmit={(event) => {
            event.preventDefault();
            if (answer !== "" && !disabled) onAnswer(answer);
          }}
        >
          <TextField
            label={options.length > 0 ? INTERVIEW_TEXTS.question.other : INTERVIEW_TEXTS.question.answer}
            value={text}
            onChange={(event) => setText(event.target.value)}
            multiline
            minRows={2}
            disabled={disabled}
            fullWidth
          />
          <div>
            <Button type="submit" variant="contained" disabled={disabled || answer === ""}>
              {INTERVIEW_TEXTS.question.send}
            </Button>
          </div>
        </form>
      ) : null}
    </div>
  );
}
