import { version } from 'os'

export const config = {
  launch: {
    width: 600,
    height: 300,
    agentDownloadUrl: '',
    winResource: {
      git: {
        version: 'v0.0.1',
        // downloadUrl:
        //   'https://www.modelscope.cn/api/v1/models/moxying/base-git-model-v0.0.1/repo?Revision=master&FilePath=git_portable_win_v0.0.1.zip'
        downloadUrl:
          'https://www.modelscope.cn/api/v1/models/moxying/base-win-model-v0.0.1/repo?Revision=master&FilePath=python_env_win_v0.0.1.zip'
      },
      pythonEnv: {
        version: 'v0.0.1',
        downloadUrl:
          'https://www.modelscope.cn/api/v1/models/moxying/base-win-model-v0.0.1/repo?Revision=master&FilePath=python_env_win_v0.0.1.zip'
      }
    }
  },
  width: 1200,
  height: 800
}
