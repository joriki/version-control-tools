  $ cat >> $HGRCPATH << EOF
  > [extensions]
  > hgmo = $TESTDIR/hgext/hgmo
  > EOF

  $ hg init repo
  $ cd repo

Empty repo is hashable

  $ hg mozrepohash
  revisions: 0 visible; 0 total
  heads: 1 visible; 1 total
  normal: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
  unfiltered: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
  phases: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
  heads: de47c9b27eb8d300dbb5f2c353e632c393262cf06340c4fa7f1b40c4cbd36f90
  unfiltered heads: de47c9b27eb8d300dbb5f2c353e632c393262cf06340c4fa7f1b40c4cbd36f90
  pushlog: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

Repo with single changeset has a hash

  $ echo 0 > foo
  $ hg -q commit -A -m initial
  $ hg mozrepohash
  revisions: 1 visible; 1 total
  heads: 1 visible; 1 total
  normal: e038fa0a8990f29ea9066d94564af8408f46a0e7c8ab123131b1fee143534e32
  unfiltered: e038fa0a8990f29ea9066d94564af8408f46a0e7c8ab123131b1fee143534e32
  phases: bf9f494d166953d7e8d2ddc24d05c3cc6613af78a052cda5bef7a9e70926e493
  heads: 8ebccd48ed6e62d5aefacbf8f4c6348e0ec12c777bff368f03163f60290c6d96
  unfiltered heads: 8ebccd48ed6e62d5aefacbf8f4c6348e0ec12c777bff368f03163f60290c6d96
  pushlog: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

Changing the phase changes the hash

  $ hg phase --public -r .
  $ hg mozrepohash
  revisions: 1 visible; 1 total
  heads: 1 visible; 1 total
  normal: e038fa0a8990f29ea9066d94564af8408f46a0e7c8ab123131b1fee143534e32
  unfiltered: e038fa0a8990f29ea9066d94564af8408f46a0e7c8ab123131b1fee143534e32
  phases: d78aadc55ac73d879f79532ec829d15d83cff06578d7d41250d090062329354e
  heads: 8ebccd48ed6e62d5aefacbf8f4c6348e0ec12c777bff368f03163f60290c6d96
  unfiltered heads: 8ebccd48ed6e62d5aefacbf8f4c6348e0ec12c777bff368f03163f60290c6d96
  pushlog: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

Adding a bookmark changes the hash

  $ hg book mymark
  $ hg mozrepohash
  revisions: 1 visible; 1 total
  heads: 1 visible; 1 total
  normal: e038fa0a8990f29ea9066d94564af8408f46a0e7c8ab123131b1fee143534e32
  unfiltered: e038fa0a8990f29ea9066d94564af8408f46a0e7c8ab123131b1fee143534e32
  phases: d78aadc55ac73d879f79532ec829d15d83cff06578d7d41250d090062329354e
  heads: 8ebccd48ed6e62d5aefacbf8f4c6348e0ec12c777bff368f03163f60290c6d96
  unfiltered heads: 8ebccd48ed6e62d5aefacbf8f4c6348e0ec12c777bff368f03163f60290c6d96
  pushlog: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855