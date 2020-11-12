FROM centos:8
MAINTAINER Harrison Totty <harrisongtotty@gmail.com>

RUN yum -y update && \
    yum -y install less vim wget epel-release && \
    yum -y install yum-utils

RUN dnf -y install \
    bash \
    diffutils \
    gcc \
    make \
    patch \
    python2 \
    python38 \
    rpm-build \
    rpm-devel \
    rpmdevtools \
    rpmlint

RUN rpmdev-setuptree

COPY .rpmmacros /root

WORKDIR /root/rpmbuild

ENTRYPOINT /bin/bash
