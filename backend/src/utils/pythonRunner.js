const { PythonShell } = require('python-shell');
const path = require('path');

class PythonRunner {
  constructor() {
    // 使用虚拟环境中的 Python
    this.pythonPath = path.join(__dirname, '../../venv/bin/python3');
    this.scriptPath = path.join(__dirname, '../../content_collab_local_llm.py');
    this.activeShells = new Map(); // 存储活动的Python shell实例
  }

  /**
   * 执行Python脚本并获取结果
   */
  async runScript(options = {}) {
    const defaultOptions = {
      mode: 'text',
      pythonPath: this.pythonPath,
      pythonOptions: ['-u'], // 不缓冲输出
      scriptPath: path.dirname(this.scriptPath),
      args: []
    };

    const pythonOptions = { ...defaultOptions, ...options };
    console.log('[PythonRunner] Running script with args:', pythonOptions.args);

    // 实际的Python脚本执行
    return new Promise((resolve, reject) => {
      let result = [];
      let error = [];
      let debugOutput = [];

      const pyshell = new PythonShell(path.basename(this.scriptPath), pythonOptions);

      pyshell.on('message', (message) => {
        try {
          if (message.startsWith('===')) {
            debugOutput.push(message);
            return;
          }
          
          const jsonResponse = JSON.parse(message);
          result.push(jsonResponse);
        } catch (e) {
          debugOutput.push(message);
        }
      });

      pyshell.on('stderr', (stderr) => {
        if (!stderr.includes('INFO') && !stderr.includes('DEBUG')) {
          console.error('[PythonRunner] Error:', stderr);
          error.push(stderr);
        }
      });

      pyshell.end((err) => {
        if (err) {
          console.error('[PythonRunner] Script error:', err.message);
          reject(err);
          return;
        }
        
        if (result.length === 0) {
          reject(new Error('No valid JSON response received from Python script'));
          return;
        }

        const response = result.length === 1 ? result[0] : result;
        console.log('[PythonRunner] Response status:', response.status);
        resolve(response);
      });
    });
  }

  /**
   * 与Python脚本进行交互式通信
   */
  async interact(sessionId, input, context = {}) {
    try {
      const inputStr = typeof input === 'object' ? JSON.stringify(input) : input;
      console.log('[PythonRunner] Processing request for session:', sessionId);

      const result = await this.runScript({
        args: [
          '--session', sessionId,
          '--input', inputStr,
          '--context', JSON.stringify(context || {})
        ]
      });

      if (!result || typeof result !== 'object') {
        throw new Error('Invalid response format from Python script');
      }

      if (!result.status) {
        result.status = 'success';
      }

      if (!result.data && result.status === 'success') {
        return {
          status: 'success',
          data: result
        };
      }

      return result;
    } catch (error) {
      console.error('[PythonRunner] Error:', error.message);
      return {
        status: 'error',
        error: {
          message: error.message,
          type: error.name
        }
      };
    }
  }
}

module.exports = new PythonRunner(); 