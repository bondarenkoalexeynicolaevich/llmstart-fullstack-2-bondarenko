/** Ответ POST /v1/auth/web-session (см. OpenAPI WebSessionCreateResponse). */
export type WebSessionCreateResponse = {
  access_token: string;
  token_type: string;
  expires_in: number;
  user_id: string;
  participant_id: string;
  role: "student" | "teacher";
  display_name: string;
};

/** Сохраняем в браузере: ответ API + flow_id из формы входа. */
export type WebClientSession = WebSessionCreateResponse & {
  flow_id: string;
};
