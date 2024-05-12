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
        sha256: 'c6e6334804777ea9239b4bfb9028beea6d98b6a9e51c0082a28aa6d01bbc6ea7'
      },
      pythonEnv: {
        version: 'v0.0.1',
        downloadUrl:
          'https://www.modelscope.cn/api/v1/models/moxying/base-win-model-v0.0.1/repo?Revision=master&FilePath=python_env_win_v0.0.1.zip',
        sha256: 'a9dc704c24b7260fb48a235fa8ed90197489f9be196661e3f87fbb5354d69bae'
      }
    }
  },
  width: 1200,
  height: 800
}
