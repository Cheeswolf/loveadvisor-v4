'use client';

import { Suspense, useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from 'next/link';
import { imageToText, ImageToTextError, analyze, AnalyzeError } from '@/lib/api';
import ResultDisplay from '@/components/ResultDisplay';
import HeroSection from '@/components/home/HeroSection';
import UrlParamHandler from '@/components/UrlParamHandler';

export default function Home() {
  // 调试输出：检查API_BASE_URL配置
  useEffect(() => {
    console.log("API_BASE_URL调试信息:");
    console.log("process.env.NEXT_PUBLIC_API_BASE_URL =", process.env.NEXT_PUBLIC_API_BASE_URL);
    console.log("实际使用的API_BASE_URL =", process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000');
    console.log("前端版本: V4-Frontend-Debug-APIBaseURL排查");
  }, []);

  // 输入模式：'text' | 'screenshot'
  const [inputMode, setInputMode] = useState<'text' | 'screenshot'>('text');
  // 文本输入内容
  const [textContent, setTextContent] = useState('');
  // 截图文件列表（真实File对象）
  const [screenshotFiles, setScreenshotFiles] = useState<File[]>([]);
  // I2确认文本
  const [confirmationText, setConfirmationText] = useState('');
  // 用户问题
  const [userQuestion, setUserQuestion] = useState('');
  // 状态提示
  const [statusMessage, setStatusMessage] = useState('等待输入内容...');
  // 加载状态
  const [loading, setLoading] = useState(false);
  // 分析加载状态
  const [analyzeLoading, setAnalyzeLoading] = useState(false);
  // 错误信息
  const [error, setError] = useState<string | null>(null);
  // 分析结果
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  // 分析请求ID（用于历史记录跳转）
  const [requestId, setRequestId] = useState<string>('');
  // 文件输入引用
  const fileInputRef = useRef<HTMLInputElement>(null);
  // 历史记录加载提示
  const [showHistoryLoadedMessage, setShowHistoryLoadedMessage] = useState(false);
  // 拖拽上传状态
  const [isDraggingOver, setIsDraggingOver] = useState(false);
  // 用于跟踪之前截图文件数量，以便在文件增加时自动触发转换
  const prevFileCountRef = useRef<number>(0);
  // 用于跟踪已转换的文件数量，避免重复触发
  const convertedFileCountRef = useRef<number>(0);

  // ========== 调试信息状态 ==========
  // 调试信息状态
  const [debugInfo, setDebugInfo] = useState({
    apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000',
    analyzeRequestState: 'idle', // 'idle' | 'preparing' | 'sending' | 'success' | 'failed'
    actualRequestUrl: '',
    requestSent: false,
    requestStartTime: null as string | null,
    requestEndTime: null as string | null,
    errorText: ''
  });


  // 通用文件处理函数（用于点击选择和拖拽上传）
  const handleFiles = (files: File[]) => {
    console.log('[Frontend] handleFiles called with', files.length, 'files');
    if (files.length === 0) return;

    // 过滤出图片文件
    const imageFiles = files.filter(file => file.type.startsWith('image/'));
    console.log('[Frontend] imageFiles filtered:', imageFiles.length);
    if (imageFiles.length === 0) {
      setError('请上传图片文件（如 PNG、JPG、JPEG、WebP 等）');
      setStatusMessage('错误：不支持的文件类型，请上传图片文件');
      return;
    }

    setScreenshotFiles(prev => [...prev, ...imageFiles]);
    setStatusMessage(`已添加 ${imageFiles.length} 个截图文件`);
    setError(null);
  };

  // 处理文件选择
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    const newFiles = Array.from(files);
    handleFiles(newFiles);

    // 清空输入值以允许重复选择相同文件
    event.target.value = '';
  };

  // 拖拽事件处理
  const handleDragEnter = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDraggingOver(true);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDraggingOver(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDraggingOver(false);

    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  };

  // 剪贴板粘贴处理
  const handlePaste = (e: React.ClipboardEvent<HTMLDivElement>) => {
    e.preventDefault();
    const clipboardData = e.clipboardData;
    if (!clipboardData) return;

    const items = clipboardData.items;
    const imageFiles: File[] = [];

    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      if (item.type.startsWith('image/')) {
        const file = item.getAsFile();
        if (file) {
          imageFiles.push(file);
        }
        // 如果 getAsFile() 返回 null，则跳过该图片项
      }
    }

    if (imageFiles.length > 0) {
      handleFiles(imageFiles);
      // 可选：设置状态提示
      setStatusMessage(`已从剪贴板粘贴 ${imageFiles.length} 个图片`);
    }
    // 如果没有图片，不执行任何操作，避免干扰文本粘贴
  };

  // 触发文件选择对话框
  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  // 移除文件
  const removeFile = (index: number) => {
    setScreenshotFiles(prev => {
      const newFiles = prev.filter((_, i) => i !== index);
      // 更新已转换文件计数：如果已转换数量大于新文件数量，则调整为新文件数量
      if (convertedFileCountRef.current > newFiles.length) {
        convertedFileCountRef.current = newFiles.length;
      }
      return newFiles;
    });
    setStatusMessage('已移除截图文件');
  };

  // 转换图片为文本
  const handleConvertToText = useCallback(async () => {
    console.log('[Frontend] handleConvertToText called with', screenshotFiles.length, 'files');
    if (screenshotFiles.length === 0) {
      setError('请先上传截图文件');
      setStatusMessage('错误：请先上传截图文件');
      return;
    }

    setLoading(true);
    setError(null);
    setStatusMessage('正在从截图中提取文字内容...');

    try {
      const response = await imageToText(screenshotFiles);

      if (response.success) {
        // 优先使用structured_chat_draft，如果为空则回退到merged_text
        const draftText = response.structured_chat_draft || response.merged_text;
        console.log('[Frontend] Setting confirmationText, length:', draftText.length, 'structured_chat_draft length:', response.structured_chat_draft?.length, 'merged_text length:', response.merged_text?.length);
        setConfirmationText(draftText);
        setStatusMessage('文字提取完成，请在下方确认并编辑文本');
        // 只有在转换成功时才更新已转换文件计数
        convertedFileCountRef.current = screenshotFiles.length;
      } else {
        setError(response.error_message || '图片处理失败');
        setStatusMessage('文字提取失败，请检查截图质量或重试');
        // 转换失败，不更新已转换文件计数
      }
    } catch (err: any) {
      const errorMessage = err.error || err.message || '请求失败';
      const errorDetail = err.detail ? `：${err.detail}` : '';
      setError(errorMessage);
      setStatusMessage('文字提取失败，请检查截图质量或重试');
      // 转换失败，不更新已转换文件计数
    } finally {
      setLoading(false);
    }
  }, [screenshotFiles]);

  // 自动触发图片转文字转换，当截图文件增加时
  useEffect(() => {
    const currentCount = screenshotFiles.length;
    const convertedCount = convertedFileCountRef.current;
    console.log('[Frontend] useEffect triggered, currentCount:', currentCount, 'convertedCount:', convertedCount, 'loading:', loading);

    // 仅在文件数量增加且当前有文件时触发，避免初始渲染和文件移除时触发
    if (currentCount > convertedCount && currentCount > 0 && !loading) {
      console.log('[Frontend] Auto-triggering handleConvertToText');
      handleConvertToText();
    }

    // 更新引用（无论是否触发，都更新 prevFileCountRef 以跟踪变化）
    prevFileCountRef.current = currentCount;
  }, [screenshotFiles, loading, handleConvertToText]);

  // 确认并开始分析
  const handleAnalyze = async () => {
    console.log('[Frontend] handleAnalyze called', { inputMode, confirmationTextLength: confirmationText.length, userQuestionLength: userQuestion.length, confirmationTextTrimmed: confirmationText.trim(), userQuestionTrimmed: userQuestion.trim() });
    if (!confirmationText.trim()) {
      setStatusMessage('文本内容为空，请输入或确认文本');
      setError('请输入待分析的文本内容');
      return;
    }
    let finalUserQuestion = userQuestion.trim();
    if (!finalUserQuestion) {
      finalUserQuestion = '分析这段对话';
      console.log('[Frontend] Using default user question:', finalUserQuestion);
    }
    if (confirmationText.trim().length < 1) {
      setStatusMessage('文本内容为空，请输入或确认文本');
      setError('请输入待分析的文本内容');
      return;
    }

    setAnalyzeLoading(true);
    setError(null);
    setRequestId('');
    setStatusMessage('正在分析对话内容，请稍候...');
    // 更新调试状态为准备中
    setDebugInfo(prev => ({
      ...prev,
      analyzeRequestState: 'preparing',
      actualRequestUrl: '',
      requestSent: false,
      requestStartTime: new Date().toISOString(),
      requestEndTime: null,
      errorText: ''
    }));

    try {
      // 更新调试状态为发送中，并设置预估的请求URL
      const apiBaseUrl = debugInfo.apiBaseUrl;
      const estimatedRequestUrl = `${apiBaseUrl}/api/v1/analyze`;
      setDebugInfo(prev => ({
        ...prev,
        analyzeRequestState: 'sending',
        actualRequestUrl: estimatedRequestUrl,
        requestSent: false, // 将在api.ts中标记为true
        errorText: ''
      }));

      console.log('[Frontend] Calling analyze API with:', { chat_text_length: confirmationText.trim().length, user_question: finalUserQuestion, provider_name: 'mock' });
      const response = await analyze({
        chat_text: confirmationText.trim(),
        user_question: finalUserQuestion,
        provider_name: 'deepseek', // 默认使用deepseek provider
        debug: false
      }, (debugInfo) => {
        // 当api.ts确认请求已发送时更新调试状态
        setDebugInfo(prev => ({
          ...prev,
          actualRequestUrl: debugInfo.actualRequestUrl,
          requestSent: debugInfo.requestSent
        }));
      });

      if (response.status === 'success') {
        // 更新调试状态为成功
        setDebugInfo(prev => ({
          ...prev,
          analyzeRequestState: 'success',
          requestSent: true,
          requestEndTime: new Date().toISOString(),
          errorText: ''
        }));
        setAnalysisResult(response.result);
        setRequestId(response.request_id);
        setStatusMessage('分析完成，结果已生成');
        setError(null);
      } else {
        // 更新调试状态为失败
        setDebugInfo(prev => ({
          ...prev,
          analyzeRequestState: 'failed',
          requestEndTime: new Date().toISOString(),
          errorText: response.error_message || '分析失败'
        }));
        setError(response.error_message || '分析失败');
        setStatusMessage('分析失败，请检查输入内容或稍后重试');
      }
    } catch (err: any) {
      const errorMessage = err.error || err.message || '分析请求失败';
      const errorDetail = err.detail ? `：${err.detail}` : '';
      // 更新调试状态为失败
      setDebugInfo(prev => ({
        ...prev,
        analyzeRequestState: 'failed',
        requestEndTime: new Date().toISOString(),
        errorText: `${errorMessage}${errorDetail}`
      }));
      setError(errorMessage);
      setStatusMessage('分析失败，请检查输入内容或稍后重试');
    } finally {
      setAnalyzeLoading(false);
    }
  };

  // 处理重新分析：清空结果并滚动到输入区域
  const handleNewAnalysis = () => {
    setAnalysisResult(null);
    setRequestId('');
    // 可选：清空确认文本和用户问题？保留现有输入以便修改
    // setConfirmationText('');
    // setUserQuestion('');
    setStatusMessage('可以修改输入内容后重新分析');

    // 滚动到输入区域
    const inputSection = document.getElementById('input-mode-section');
    if (inputSection) {
      inputSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  // 处理反馈
  const handleFeedback = (helpful: boolean) => {
    console.log(`用户反馈：${helpful ? '有帮助' : '无帮助'}`);
    // 在实际应用中，这里可以发送到后端
    alert(`感谢您的反馈！分析工具会持续改进。`);
  };

  // 获取文件名用于显示
  const getFileDisplayName = (file: File) => {
    return file.name || `screenshot_${file.size}.png`;
  };

  // 计算结果展示区状态
  const resultStatus = analyzeLoading ? 'loading' :
    error ? 'error' :
    analysisResult ? 'success' : 'idle';

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Hero区域 */}
        <HeroSection />

        {/* URL参数处理器 - 用于读取chat_text和user_question参数 */}
        <Suspense fallback={null}>
          <UrlParamHandler
            setConfirmationText={setConfirmationText}
            setTextContent={setTextContent}
            setUserQuestion={setUserQuestion}
            setInputMode={setInputMode}
            setShowHistoryLoadedMessage={setShowHistoryLoadedMessage}
          />
        </Suspense>

        {/* 顶部导航栏 */}
        <header className="mb-8 text-center">
          <div className="flex justify-center space-x-4">
            <Link
              href="/history"
              className="px-4 py-2 bg-purple-100 text-purple-700 rounded-md font-medium hover:bg-purple-200 transition-colors"
            >
              查看历史记录
            </Link>
            <button
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md font-medium hover:bg-gray-200 transition-colors cursor-not-allowed"
              disabled
            >
              用户设置（待开发）
            </button>
          </div>
          <div className="mt-4 text-sm text-gray-500">
            <p>LoveAdvisor V4 正式用户端 · 基于AI的情感分析与决策辅助工具</p>
          </div>
        </header>

        <div className="flex flex-col gap-8">
          {/* 输入区域 */}
          <div className="space-y-8">
            {/* 输入模式区 */}
            <section id="input-mode-section" className="bg-white rounded-xl shadow-md p-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">输入模式区</h2>
              <p className="text-gray-600 mb-4">选择适合您的方式：直接输入文本或上传聊天截图，系统将自动处理。</p>
              <div className="space-y-6">
                {/* 模式切换按钮 */}
                <div className="flex space-x-4">
                  <button
                    className={`flex-1 py-3 rounded-md font-medium ${inputMode === 'text' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700'}`}
                    onClick={() => setInputMode('text')}
                  >
                    文本输入模式
                  </button>
                  <button
                    className={`flex-1 py-3 rounded-md font-medium ${inputMode === 'screenshot' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700'}`}
                    onClick={() => setInputMode('screenshot')}
                  >
                    截图上传模式
                  </button>
                </div>

                {/* 文本输入区域 */}
                {inputMode === 'text' && (
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-8">
                    <p className="text-gray-500 mb-2 text-center">文本输入区域</p>
                    <p className="text-sm text-gray-600 mb-4 text-center">
                      直接输入对话文本或粘贴聊天记录，获得情感倾向分析和关系发展建议。
                    </p>
                    <textarea
                      className="w-full h-48 p-3 border border-gray-300 rounded-md"
                      placeholder="请输入情感咨询问题或对话内容..."
                      value={textContent}
                      onChange={(e) => setTextContent(e.target.value)}
                    />
                    <div className="mt-4 text-sm text-gray-500">
                      <p>当前字符数：{textContent.length}（最大支持5000字符）</p>
                    </div>
                    <div className="mt-4 flex justify-center">
                      <button
                        className="px-4 py-2 bg-blue-100 text-blue-700 rounded-md text-sm hover:bg-blue-200"
                        onClick={() => {
                          if (textContent.trim()) {
                            setConfirmationText(textContent);
                            setStatusMessage('文本已就绪，请在下方确认并输入您的问题');
                          } else {
                            setStatusMessage('文本内容为空，无法复制');
                          }
                        }}
                      >
                        使用此文本进行分析
                      </button>
                    </div>
                  </div>
                )}

                {/* 截图上传区域 */}
                {inputMode === 'screenshot' && (
                  <div
                    className={`border-2 border-dashed rounded-lg p-8 ${isDraggingOver ? 'border-blue-500 bg-blue-50' : 'border-gray-300'}`}
                    onDragEnter={handleDragEnter}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    onPaste={handlePaste}
                    tabIndex={0}
                    role="region"
                    aria-label="截图上传区域，支持点击选择、拖拽上传和粘贴剪贴板图片"
                  >
                    <p className="text-gray-500 mb-2 text-center">截图上传区域</p>
                    <p className="text-sm text-gray-600 mb-4 text-center">
                      上传聊天截图，自动提取文字内容。支持微信、QQ等主流聊天应用的截图识别。
                    </p>
                    <div className="space-y-6">
                      {/* 隐藏的文件输入 */}
                      <input
                        type="file"
                        ref={fileInputRef}
                        onChange={handleFileSelect}
                        className="hidden"
                        multiple
                        accept="image/*"
                      />

                      {/* 上传按钮 */}
                      <div className="flex items-center justify-center">
                        <button
                          className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                          onClick={triggerFileInput}
                          disabled={loading}
                        >
                          选择聊天截图
                        </button>
                      </div>
                      <p className="text-sm text-gray-400 text-center">支持 JPEG、PNG、GIF、BMP、WebP 格式，最多10张图片</p>
                      <p className="text-sm text-blue-500 text-center">或将图片文件拖拽到此处上传</p>
                      <p className="text-sm text-green-500 text-center">或直接粘贴剪贴板中的截图（Ctrl+V）</p>

                      {/* 已上传图片列表 */}
                      {screenshotFiles.length > 0 ? (
                        <div className="mt-6">
                          <h3 className="font-medium text-gray-700 mb-2">已上传截图：</h3>
                          <ul className="space-y-2">
                            {screenshotFiles.map((file, index) => (
                              <li key={index} className="flex items-center justify-between bg-gray-50 p-3 rounded-md">
                                <span className="text-gray-700 truncate">{getFileDisplayName(file)} ({Math.round(file.size / 1024)} KB)</span>
                                <button
                                  className="text-sm text-red-500 hover:text-red-700"
                                  onClick={() => removeFile(index)}
                                  disabled={loading}
                                >
                                  移除
                                </button>
                              </li>
                            ))}
                          </ul>
                        </div>
                      ) : (
                        <div className="text-center py-4 text-gray-400">
                          暂无上传截图
                        </div>
                      )}

                      {/* 错误提示 */}
                      {error && (
                        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                          <p className="text-sm text-red-700">{error}</p>
                        </div>
                      )}

                      {/* 提取文字内容按钮 */}
                      <div className="flex justify-center mt-6">
                        <button
                          className={`px-6 py-3 rounded-md font-medium ${loading ? 'bg-gray-300 text-gray-500 cursor-not-allowed' : 'bg-green-600 text-white hover:bg-green-700'}`}
                          onClick={handleConvertToText}
                          disabled={loading || screenshotFiles.length === 0}
                        >
                          {loading ? (
                            <span className="flex items-center">
                              <svg className="animate-spin h-4 w-4 mr-2 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                              </svg>
                              正在提取文字...
                            </span>
                          ) : '提取文字内容'}
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </section>

            {/* I2文本确认区 */}
            <section className="bg-white rounded-xl shadow-md p-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">I2文本确认区</h2>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8">
                <p className="text-gray-500 mb-2 text-center">确认并编辑待分析文本</p>
                <div className="mb-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-blue-800 mb-2">
                    <span className="font-medium">为什么需要确认文本？</span> 截图转文字可能因图像质量、字体等原因存在识别误差。请检查并修正提取的文本，确保分析依据准确。
                  </p>
                  <p className="text-sm text-blue-800">
                    <span className="font-medium">分析结果边界：</span> 本工具仅为辅助决策参考，分析基于您提供的对话内容。现实沟通与真诚交流才是关系发展的基石。
                  </p>
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">用户问题</label>
                  <input
                    type="text"
                    className="w-full p-3 border border-gray-300 rounded-md"
                    placeholder="请输入您关于这段对话的具体问题或关切..."
                    value={userQuestion}
                    onChange={(e) => setUserQuestion(e.target.value)}
                  />
                  <p className="text-xs text-gray-500 mt-1">例如：他/她对我有好感吗？我们目前处于什么阶段？</p>
                </div>
                <textarea
                  className="w-full h-48 p-3 border border-gray-300 rounded-md"
                  placeholder="在此处确认或编辑从截图提取的文本，或直接输入情感咨询内容..."
                  value={confirmationText}
                  onChange={(e) => setConfirmationText(e.target.value)}
                />
                <div className="mt-4 text-sm text-gray-500">
                  <p>当前字符数：{confirmationText.length}（建议不少于50字符）</p>
                </div>

                {/* 历史记录加载提示 */}
                {showHistoryLoadedMessage && (
                  <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
                    <p className="text-sm text-green-700">已载入历史分析内容，您可以编辑后重新分析</p>
                  </div>
                )}

                {/* 状态提示文案占位 */}
                <div className={`mt-4 p-3 rounded-md ${error ? 'bg-red-50 border border-red-200' : 'bg-blue-50'}`}>
                  <p className={`text-sm ${error ? 'text-red-700' : 'text-blue-700'}`}>{statusMessage}</p>
                </div>

                <div className="mt-6 flex space-x-4 justify-center">
                  <button
                    className={`px-6 py-2 rounded-md font-medium ${analyzeLoading ? 'bg-gray-300 text-gray-500 cursor-not-allowed' : 'bg-green-600 text-white hover:bg-green-700'}`}
                    onClick={handleAnalyze}
                    disabled={analyzeLoading || !confirmationText.trim()}
                  >
                    {analyzeLoading ? (
                      <span className="flex items-center">
                        <svg className="animate-spin h-4 w-4 mr-2 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        正在分析中...
                      </span>
                    ) : '开始情感分析'}
                  </button>
                  <button
                    className="px-6 py-2 bg-red-100 text-red-700 rounded-md font-medium hover:bg-red-200"
                    onClick={() => {
                      // 清空确认文本和用户问题，同时清除分析结果和请求ID
                      setConfirmationText('');
                      setUserQuestion('');
                      setAnalysisResult(null);
                      setRequestId('');
                      setStatusMessage('内容已清空，请重新输入或上传截图');
                    }}
                  >
                    清空重试
                  </button>
                </div>
              </div>
            </section>
          </div>

          {/* 结果展示区 */}
          <div className="w-full">
            <section className="bg-white rounded-xl shadow-md p-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">结果展示区</h2>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 min-h-[500px] overflow-y-auto min-w-0 break-words">
                <div className="mb-4 bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                  <p className="text-sm text-yellow-800">
                    <span className="font-medium">请注意：</span> 分析结果仅为辅助判断参考，不替代现实沟通与专业咨询。
                  </p>
                </div>
                <ResultDisplay
                  result={analysisResult}
                  status={resultStatus}
                  errorMessage={error || undefined}
                  requestId={requestId}
                  onNewAnalysis={handleNewAnalysis}
                  onFeedback={handleFeedback}
                />

                <div className="mt-8 flex justify-center">
                  <button className="px-6 py-3 bg-purple-100 text-purple-700 rounded-md font-medium cursor-not-allowed" disabled>
                    查看详细报告
                  </button>
                </div>
              </div>
            </section>
          </div>
        </div>

        {/* 调试信息区域 - 用于排查API请求 */}
        <div className="mt-8 p-4 bg-gray-900 text-gray-100 rounded-lg font-mono text-sm">
          <h3 className="text-lg font-bold mb-2 text-yellow-300">API请求调试信息</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p><span className="text-gray-400">API_BASE_URL:</span> <span className="text-green-300">{debugInfo.apiBaseUrl}</span></p>
              <p><span className="text-gray-400">分析请求状态:</span> <span className={`font-bold ${
                debugInfo.analyzeRequestState === 'idle' ? 'text-gray-300' :
                debugInfo.analyzeRequestState === 'preparing' ? 'text-blue-300' :
                debugInfo.analyzeRequestState === 'sending' ? 'text-yellow-300' :
                debugInfo.analyzeRequestState === 'success' ? 'text-green-300' :
                'text-red-300'
              }`}>{debugInfo.analyzeRequestState}</span></p>
              <p><span className="text-gray-400">请求是否已发送:</span> <span className={debugInfo.requestSent ? "text-green-300" : "text-red-300"}>{debugInfo.requestSent ? "是" : "否"}</span></p>
            </div>
            <div>
              <p><span className="text-gray-400">实际请求URL:</span> <span className="text-blue-300 break-all">{debugInfo.actualRequestUrl || "未设置"}</span></p>
              <p><span className="text-gray-400">请求开始时间:</span> <span className="text-gray-300">{debugInfo.requestStartTime || "未开始"}</span></p>
              <p><span className="text-gray-400">请求结束时间:</span> <span className="text-gray-300">{debugInfo.requestEndTime || "未结束"}</span></p>
              <p><span className="text-gray-400">错误信息:</span> <span className="text-red-300">{debugInfo.errorText || "无"}</span></p>
            </div>
          </div>
          <div className="mt-4 pt-2 border-t border-gray-700">
            <p className="text-gray-400 text-xs">说明：此区域仅用于调试，显示分析请求的真实状态。点击"开始情感分析"按钮后观察状态变化。</p>
          </div>
        </div>

        {/* 底部状态提示 */}
        <footer className="mt-12 pt-8 border-t text-center text-gray-500 text-sm">
          <p>LoveAdvisor V4 前端细化占位版本 1.2 | 开发阶段：Phase4-MTU5 | 最后更新：2026-04-18</p>
          <p className="mt-2">此版本已添加历史记录页面功能，可通过顶部按钮访问分析历史。</p>
        </footer>
      </div>
    </div>
  );
}
