export const config = {
  launch: {
    width: 600,
    height: 300,
    agentDownloadUrl: '',
    winResource: {
      git: {
        version: 'v0.0.1',
        downloadUrl:
          'https://www.modelscope.cn/api/v1/models/moxying/base-git-model-v0.0.1/repo?Revision=master&FilePath=git_portable_win_v0.0.1.zip',
        sha256: 'de21d1452c6bf90f5b9d76185dacc7299937bad38b4606e8b3278bdf15918c1f'
      },
      pythonEnv: {
        version: 'v0.0.1',
        downloadUrl:
          'https://www.modelscope.cn/api/v1/models/moxying/base-win-model-v0.0.1/repo?Revision=master&FilePath=python_env_win_v0.0.1.zip',
        sha256: 'd201cb727b84bbfe6186156371bb446b203b57d98aa83522a0152825f6ef593d'
      }
    }
  },
  width: 1200,
  height: 800
}
