export type Video = {
  id: string;
  title: string;
  description: string;
  thumbnailUrl: string;
  embedUrl: string;
  category: string;
  duration: string;
  tags?: string[];
  views?: number;
  uploadedAt?: string;
};
