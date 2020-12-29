#!/usr/bin/env bats

export REPHILE_CACHE=$(pwd)/rephile-test.db

setup_file () {
    rm -f $REPHILE_CACHE
}

@test "have exiftool" {
    run exiftool
}

@test "have rephile" {
    run rephile 
}

@test "direct exif" {
    run rephile exif images/viren.jpg
    echo "$output"
    [[ "$(echo -e "$output"|grep SourceFile|grep -c viren.jpg)" = "1" ]]
}

@test "direct hashsize" {
    run rephile hashsize images/viren.jpg
    out=($output)
    echo "$output"
    [[ "${out[0]}" = "32460" ]]
    [[ "${out[1]}" = "c151a789826f025835c9b5ad2dec134599894f238214c42447b833d7d7aa1fbd" ]]
    [[ "${out[2]}" = "images/viren.jpg" ]]
}

@test "render digests" {
    run rephile render -t test/dump-digests.txt.j2 \
        images/{moon,viren,viren2}.jpg
    h1="030d30c1934372f6999016af345fa2c82092363a6fd7b791b3c4c45757244760"
    h2="c151a789826f025835c9b5ad2dec134599894f238214c42447b833d7d7aa1fbd"
    echo "h1 = $h1"
    echo "h2 = $h2"
    echo "$output"
    [[ "$(echo -e "$output"|grep -c $h1)" = "2" ]]
    [[ "$(echo -e "$output"|grep -c $h2)" = "3" ]]
}

teardown_file () {
    rm -f $REPHILE_CACHE
}
