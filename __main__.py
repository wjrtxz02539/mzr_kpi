from gevent.monkey import patch_all
patch_all()
import sys
from gevent import sleep

from app import Control, walk_space

if __name__ == '__main__':
    Control.from_json_file(sys.argv[1])
    Control.init()

    while True:
        walk_space(user_id=Control.bili_user_id, skip=Control.skip, max_depth=Control.depth, force=Control.force,
                   last_days=Control.last_days)
        sleep(60)
