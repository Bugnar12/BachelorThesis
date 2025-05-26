import {Prediction} from './prediction';

export interface Email {
  email_id: number;
  email_subject: string;
  email_sender: string;
  email_recipient: string;
  email_body: string;
  email_timestamp: string;
  text_prediction?: string | Prediction;
  url_prediction?: string | Prediction;
  vt_domain_result?: string;
}
