#!/usr/bin/env bats

export rdb=""

setup_file () {
    rm -f rephile-test.db
}

@test "have exiftool" {
    run exiftool
}

@test "have rephile" {
    run rephile 
}

@test "direct exif" {
    run rephile exif viren.jpg
}

@test "direct hashsize" {
    run rephile hashsize images/viren.jpg
    out=($output)
    echo "$output"
    [[ "${out[0]}" = "32460" ]]
    [[ "${out[1]}" = "c151a789826f025835c9b5ad2dec134599894f238214c42447b833d7d7aa1fbd" ]]
    [[ "${out[2]}" = "images/viren.jpg" ]]
}

teardown_file () {
    rm -f rephile-test.db
}


