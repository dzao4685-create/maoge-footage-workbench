# 素材库

包含17个商品、48条回放入口及完整历史资料；外部盘原录像未上传。

商品可置顶，商品日期支持手动添加、删除、恢复。使用Cloudflare D1进行多设备同步；修改需要管理密码。

Cloudflare Pages构建 python3 build-site.py，输出public。生产环境绑定D1变量 ORGANIZER_DB，并配置Secret ORGANIZER_PASSWORD。密码不能提交GitHub。
