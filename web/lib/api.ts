/**
 * LoveAdvisor V4 Frontend API Client
 *
 * This module provides functions to interact with the LoveAdvisor V4 backend API.
 * Currently only includes the I1 image-to-text endpoint.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';
console.log('[API Client] API_BASE_URL initialized:', API_BASE_URL);
console.log('[API Client] process.env.NEXT_PUBLIC_API_BASE_URL:', process.env.NEXT_PUBLIC_API_BASE_URL);
console.log('[API Client] Using fallback?', !process.env.NEXT_PUBLIC_API_BASE_URL ? 'YES - using default http://127.0.0.1:8000' : 'NO - using env var');

export interface ImageToTextResponse {
  success: boolean;
  raw_text: string;
  merged_text: string;
  structured_chat_draft: string;
  provider: string;
  source_type: string;
  image_count: number;
  need_user_confirm: boolean;
  error_message: string;
  request_id?: string;
  metadata?: Record<string, any>;
}

export interface ImageToTextError {
  error: string;
  detail?: string;
}

/**
 * Convert uploaded images to text using the I1 image-to-text endpoint.
 *
 * @param images - Array of File objects representing uploaded images
 * @param provider - Text extraction provider (default: "qwen_ocr")
 * @param source_type - Source type identifier (default: "image")
 * @param request_id - Optional request ID for tracking
 * @returns Promise resolving to ImageToTextResponse
 * @throws {ImageToTextError} If the request fails or returns an error
 */
export async function imageToText(
  images: File[],
  provider: string = 'qwen_ocr',
  source_type: string = 'image',
  request_id?: string
): Promise<ImageToTextResponse> {
  console.log('[I1 API] Calling /api/v1/image-to-text with', images.length, 'images');
  console.log('[I1 API] API_BASE_URL =', API_BASE_URL);
  console.log('[I1 API] Full request URL =', `${API_BASE_URL}/api/v1/image-to-text`);
  // Validate input
  if (!images || images.length === 0) {
    throw {
      error: 'No images provided',
      detail: 'Please select at least one image to process.'
    };
  }

  if (images.length > 10) {
    throw {
      error: 'Too many images',
      detail: 'Maximum 10 images allowed per request.'
    };
  }

  // Create FormData for multipart upload
  const formData = new FormData();

  // Append each image file
  images.forEach((image, index) => {
    formData.append('images', image);
  });

  // Append query parameters as form fields
  formData.append('provider', provider);
  formData.append('source_type', source_type);
  if (request_id) {
    formData.append('request_id', request_id);
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/image-to-text`, {
      method: 'POST',
      body: formData,
      // Note: Do not set Content-Type header for FormData - browser will set it automatically
      // with correct boundary
    });

    const data = await response.json();

    if (!response.ok) {
      // Handle HTTP error status
      throw {
        error: `Request failed with status ${response.status}`,
        detail: data.detail || data.error_message || 'Unknown error'
      };
    }

    // Validate response structure
    if (!data.success) {
      console.error('[I1 API] Image processing failed:', data.error_message);
      throw {
        error: data.error_message || 'Image processing failed',
        detail: 'The image-to-text conversion was unsuccessful.'
      };
    }

    console.log('[I1 API] Success, merged_text length:', data.merged_text?.length);
    return data as ImageToTextResponse;
  } catch (error: any) {
    // Re-throw structured errors
    if (error.error) {
      throw error;
    }

    // Handle network or parsing errors
    throw {
      error: 'Network or server error',
      detail: error.message || 'Failed to connect to the server.'
    };
  }
}

/**
 * Utility function to check if the API is reachable
 */
export async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/health`);
    return response.ok;
  } catch {
    return false;
  }
}

/**
 * Analyze request and response interfaces
 */
export interface AnalyzeRequest {
  chat_text: string;
  user_question: string;
  provider_name?: string;
  debug?: boolean;
  request_id?: string;
  context?: Record<string, any>;
  config_overrides?: Record<string, any>;
}

export interface AnalyzeResult {
  relationship_stage: string;
  interest_level: string;
  psychological_analysis: string;
  risk_points: string[];
  suggestions: string[];
  next_step: string;
  debug?: Record<string, any>;
}

export interface AnalyzeResponse {
  request_id: string;
  status: string;
  result: AnalyzeResult;
  error_message: string;
  metadata: Record<string, any>;
}

export interface AnalyzeError {
  error: string;
  detail?: string;
}

/**
 * Submit text for analysis using the main analysis endpoint
 *
 * @param request - Analysis request containing chat text and user question
 * @returns Promise resolving to AnalyzeResponse
 * @throws {AnalyzeError} If the request fails or returns an error
 */
export async function analyze(
  request: AnalyzeRequest,
  debugCallback?: (debugInfo: { actualRequestUrl: string, requestSent: boolean }) => void
): Promise<AnalyzeResponse> {
  console.log('[Analyze API] API_BASE_URL =', API_BASE_URL);
  const actualRequestUrl = `${API_BASE_URL}/api/v1/analyze`;
  console.log('[Analyze API] Full request URL =', actualRequestUrl);
  // Validate input
  if (!request.chat_text || request.chat_text.trim().length === 0) {
    throw {
      error: 'No chat text provided',
      detail: 'Please provide conversation text to analyze.'
    };
  }

  if (!request.user_question || request.user_question.trim().length === 0) {
    throw {
      error: 'No user question provided',
      detail: 'Please provide a question or concern about the relationship.'
    };
  }

  // Prepare request body with defaults
  const body = {
    chat_text: request.chat_text.trim(),
    user_question: request.user_question.trim(),
    provider_name: request.provider_name || 'deepseek',
    debug: request.debug || false,
    request_id: request.request_id,
    context: request.context || {},
    config_overrides: request.config_overrides || {}
  };

  try {
    // 调试信息：请求即将发送
    if (debugCallback) {
      debugCallback({
        actualRequestUrl: actualRequestUrl,
        requestSent: true
      });
    }

    const response = await fetch(actualRequestUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();

    if (!response.ok) {
      // Handle HTTP error status
      throw {
        error: `Request failed with status ${response.status}`,
        detail: data.detail || data.error_message || 'Unknown error'
      };
    }

    // Validate response structure
    if (!data.status) {
      throw {
        error: 'Invalid response format',
        detail: 'The server returned an unexpected response format.'
      };
    }

    if (data.status === 'error') {
      throw {
        error: data.error_message || 'Analysis failed',
        detail: 'The analysis pipeline returned an error.'
      };
    }

    return data as AnalyzeResponse;
  } catch (error: any) {
    // Re-throw structured errors
    if (error.error) {
      throw error;
    }

    // Handle network or parsing errors
    throw {
      error: 'Network or server error',
      detail: error.message || 'Failed to connect to the server.'
    };
  }
}

/**
 * History record interfaces and functions
 */

export interface HistoryRecord {
  request_id: string;
  relationship_stage: string;
  interest_level: string;
  next_step: string;
  created_at: string;
  user_question?: string;
  provider_name?: string;
}

export interface FullHistoryRecord extends HistoryRecord {
  chat_text: string;
  psychological_analysis?: string;
  risk_points?: string[];
  suggestions: string[];
  debug?: Record<string, any>;
}

export interface HistoryResponse {
  count: number;
  records: HistoryRecord[];
  limit: number;
}

export interface HistoryError {
  error: string;
  detail?: string;
}

/**
 * Retrieve analysis history records from the backend.
 *
 * @param limit - Maximum number of records to retrieve (default 20, max 100)
 * @returns Promise resolving to HistoryResponse
 * @throws {HistoryError} If the request fails or returns an error
 */
export async function getHistory(limit: number = 20): Promise<HistoryResponse> {
  // Validate limit parameter
  if (limit <= 0) limit = 20;
  if (limit > 100) limit = 100;

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/history?limit=${limit}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    const data = await response.json();

    if (!response.ok) {
      // Handle HTTP error status
      throw {
        error: `Request failed with status ${response.status}`,
        detail: data.detail || data.error_message || 'Unknown error'
      };
    }

    return data as HistoryResponse;
  } catch (error: any) {
    // Re-throw structured errors
    if (error.error) {
      throw error;
    }

    // Handle network or parsing errors
    throw {
      error: 'Network or server error',
      detail: error.message || 'Failed to connect to the server.'
    };
  }
}

/**
 * Retrieve a specific analysis record by request_id.
 *
 * @param request_id - The unique identifier of the analysis request
 * @returns Promise resolving to FullHistoryRecord
 * @throws {HistoryError} If the request fails or returns an error
 */
export async function getHistoryRecord(request_id: string): Promise<FullHistoryRecord> {
  if (!request_id || request_id.trim().length === 0) {
    throw {
      error: 'No request_id provided',
      detail: 'Please provide a valid request_id to retrieve the record.'
    };
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/history/${encodeURIComponent(request_id)}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    const data = await response.json();

    if (!response.ok) {
      // Handle HTTP error status
      throw {
        error: `Request failed with status ${response.status}`,
        detail: data.detail || data.error_message || 'Record not found'
      };
    }

    return data as FullHistoryRecord;
  } catch (error: any) {
    // Re-throw structured errors
    if (error.error) {
      throw error;
    }

    // Handle network or parsing errors
    throw {
      error: 'Network or server error',
      detail: error.message || 'Failed to connect to the server.'
    };
  }
}