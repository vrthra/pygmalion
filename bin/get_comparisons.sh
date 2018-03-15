tst=$1
shift 1
env PREFIX="$1" python3 gencmd.py $tst
