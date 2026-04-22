import React from 'react';
import Link from 'next/link';

interface HeroSectionProps {
  // 可以添加props，但目前不需要
}

const HeroSection: React.FC<HeroSectionProps> = () => {
  return (
    <div className="w-full bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl shadow-lg p-8 md:p-12 mb-12 border border-gray-200">
      <div className="max-w-4xl mx-auto text-center">
        {/* 主标题 */}
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
          LoveAdvisor 情感分析助手
        </h1>

        {/* 副标题 */}
        <p className="text-xl md:text-2xl text-gray-700 mb-6 max-w-3xl mx-auto">
          基于AI的恋爱对话分析与决策辅助工具
        </p>

        {/* 功能说明 */}
        <div className="bg-white rounded-xl p-6 mb-8 shadow-sm border border-gray-100">
          <div className="flex flex-col md:flex-row justify-center items-center md:items-start gap-8 mb-6">
            {/* 截图分析 */}
            <div className="flex-1 max-w-md">
              <div className="flex items-center mb-3">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-800">截图分析</h3>
              </div>
              <p className="text-gray-600 text-left">
                上传聊天截图，自动提取文字内容。支持微信、QQ等主流聊天应用的截图识别。
              </p>
            </div>

            {/* 文本分析 */}
            <div className="flex-1 max-w-md">
              <div className="flex items-center mb-3">
                <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mr-3">
                  <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-800">文本分析</h3>
              </div>
              <p className="text-gray-600 text-left">
                直接输入对话文本，获得情感倾向分析和关系发展建议。
              </p>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-blue-800 font-medium text-center">
              💡 两种方式任选其一，获得专业的AI分析报告
            </p>
          </div>
        </div>

        {/* 风险边界提示 */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6 mb-8">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="w-6 h-6 text-yellow-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.346 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
              </svg>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-yellow-800 mb-2">重要提示</h3>
              <p className="text-yellow-700">
                LoveAdvisor 仅为辅助决策工具，分析结果基于您提供的对话内容。请勿完全依赖AI判断，
                <span className="font-semibold">现实沟通与真诚交流</span>才是关系发展的基石。本工具不替代专业心理咨询，如遇严重情感问题，请寻求专业帮助。
              </p>
            </div>
          </div>
        </div>

        {/* 开始入口 */}
        <div className="space-y-4">
          <h3 className="text-xl font-semibold text-gray-800">开始分析</h3>
          <p className="text-gray-600 max-w-2xl mx-auto">
            选择下方任一方式开始，几分钟内即可获得详细的情感分析报告。
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4 pt-4">
            <a
              href="#input-mode-section"
              className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all duration-300 shadow-md hover:shadow-lg text-lg"
            >
              立即开始分析 →
            </a>
            <Link
              href="/history"
              className="px-8 py-4 bg-white text-gray-700 font-semibold rounded-xl border-2 border-gray-300 hover:bg-gray-50 transition-colors duration-300 text-lg"
            >
              查看历史分析
            </Link>
          </div>
          <p className="text-sm text-gray-500 mt-4">
            无需注册，立即使用 · 免费分析 · 隐私保护
          </p>
        </div>
      </div>
    </div>
  );
};

export default HeroSection;